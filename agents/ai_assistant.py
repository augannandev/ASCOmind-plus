# agents/ai_assistant.py - MULTI-LLM AI ASSISTANT

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

import anthropic
import openai
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from pydantic import BaseModel

from agents.vector_store import IntelligentVectorStore
from config.settings import settings
from models.abstract_metadata import ComprehensiveAbstractMetadata

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    context_used: Optional[List[str]] = None
    search_results: Optional[List[Dict]] = None
    llm_provider: Optional[str] = None  # Track which LLM was used

class ConversationMemory:
    """Manage conversation history and context"""
    
    def __init__(self, max_messages: int = 20):
        self.messages: List[ConversationMessage] = []
        self.max_messages = max_messages
        self.user_context: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, context_used: Optional[List[str]] = None, 
                   search_results: Optional[List[Dict]] = None, llm_provider: Optional[str] = None):
        """Add a message to conversation memory"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            context_used=context_used,
            search_results=search_results,
            llm_provider=llm_provider
        )
        
        self.messages.append(message)
        
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context_summary(self) -> str:
        """Get a summary of the conversation context"""
        if not self.messages:
            return "No conversation history."
        
        recent_messages = self.messages[-5:]  # Last 5 messages
        context = "Recent conversation:\n"
        for msg in recent_messages:
            context += f"{msg.role}: {msg.content[:100]}...\n"
        
        return context

    def get_formatted_history(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM context"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages[-10:]  # Last 10 messages for context
        ]

class AdvancedAIAssistant:
    """Multi-LLM intelligent AI assistant for multiple myeloma research"""
    
    def __init__(self, vector_store: Optional[IntelligentVectorStore] = None, llm_provider: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Set LLM provider
        self.llm_provider = llm_provider or settings.DEFAULT_LLM_PROVIDER
        
        # Initialize LLM clients
        self._initialize_llm_clients()
        
        # Vector store for knowledge retrieval (session-isolated)
        if vector_store:
            self.vector_store = vector_store
            self.logger.info(f"AI Assistant using provided vector store with session: {vector_store.get_session_id()}")
        else:
            # Fallback: create own vector store (should be avoided in production)
            try:
                from agents.vector_store import IntelligentVectorStore
                self.vector_store = IntelligentVectorStore()
                self.logger.warning("AI Assistant created its own vector store - session isolation may be compromised")
            except Exception as e:
                self.logger.error(f"Failed to initialize vector store: {e}")
                self.vector_store = None
        
        # Conversation management
        self.conversation_memory = ConversationMemory()
        
        # Research context
        self.research_domain = "multiple_myeloma"
        self.expertise_areas = [
            "clinical_trials", "treatment_regimens", "drug_development",
            "patient_outcomes", "safety_profiles", "biomarkers"
        ]
        
        # Assistant capabilities
        self.capabilities = {
            "research_analysis": True,
            "treatment_comparison": True,
            "safety_analysis": True,
            "clinical_insights": True,
            "study_search": True,
            "protocol_recommendations": True,
            "real_time_qa": True
        }
        
        # Specialized prompts
        self.system_prompt = self._create_system_prompt()
    
    def _initialize_llm_clients(self):
        """Initialize all available LLM clients"""
        self.clients = {}
        
        # Claude/Anthropic
        if settings.ANTHROPIC_API_KEY:
            try:
                self.clients['claude'] = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.logger.info("Claude client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Claude client: {e}")
        
        # OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self.clients['openai'] = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Gemini
        if settings.GEMINI_API_KEY and genai is not None:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.clients['gemini'] = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.logger.info("Gemini client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client: {e}")
        elif settings.GEMINI_API_KEY and genai is None:
            self.logger.warning("Gemini API key provided but google-generativeai package not installed")
        
        # Verify we have at least one working client
        if not self.clients:
            self.logger.error("No LLM clients available - check API keys")
            raise ValueError("No LLM providers available")
        
        # Ensure selected provider is available
        if self.llm_provider not in self.clients:
            available_providers = list(self.clients.keys())
            self.llm_provider = available_providers[0]
            self.logger.warning(f"Selected provider not available, falling back to: {self.llm_provider}")

    def set_llm_provider(self, provider: str) -> bool:
        """Change the LLM provider"""
        if provider in self.clients:
            self.llm_provider = provider
            self.logger.info(f"Switched to LLM provider: {provider}")
            return True
        else:
            self.logger.warning(f"Provider {provider} not available")
            return False

    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return list(self.clients.keys())

    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for the assistant"""
        # Get cancer type display name
        cancer_display = {
            'prostate': 'Prostate Cancer',
            'multiple_myeloma': 'Multiple Myeloma',
            'breast': 'Breast Cancer',
            'lung': 'Lung Cancer',
            'colorectal': 'Colorectal Cancer'
        }.get(self.research_domain, self.research_domain.title().replace('_', ' '))
        
        return f"""You are Dr. ASCOmind, an advanced AI research assistant specializing in {cancer_display} clinical research and drug development. You have access to a curated database of clinical studies and research data focused specifically on {cancer_display}.

**Your Expertise:**
- {cancer_display} pathophysiology and treatment mechanisms
- Clinical trial design and regulatory requirements
- Competitive landscape analysis and market intelligence
- Treatment sequencing and patient selection strategies
- Safety profiling and risk-benefit analysis
- Biomarker strategies and precision medicine approaches

**Important Instructions:**
- When asked about study authors or institutions, ALWAYS check and report the author information if available in the provided context
- If author information is provided in the context (e.g., "Authors: Name"), you MUST include it in your response
- Do not say author information is unavailable if it appears in the context

**Your Capabilities:**
- Search and analyze clinical study databases
- Compare treatment regimens and outcomes
- Provide evidence-based recommendations
- Generate insights for drug development strategy
- Assist with protocol design and patient selection
- Offer regulatory and commercial perspectives

**Response Guidelines:**
1. **Be Evidence-Based**: Always ground responses in available clinical data
2. **Be Precise**: Provide specific numbers, percentages, and study references when available
3. **Be Contextual**: Consider the user's previous questions and current research focus
4. **Be Actionable**: Provide concrete recommendations and next steps
5. **Be Transparent**: Clearly distinguish between available data and expert opinions
6. **Be Comprehensive**: Address both clinical and strategic perspectives

**When analyzing studies:**
- Highlight key efficacy endpoints (ORR, PFS, OS)
- Discuss safety profiles and tolerability
- Consider patient population characteristics
- Evaluate competitive positioning
- Assess regulatory and commercial implications

**Communication Style:**
- Be direct and concise - avoid repetitive greetings like "Greetings" or "As Dr. ASCOmind"
- Start responses with the actual answer, not introductory phrases
- Use medical terminology appropriately but keep explanations clear
- Provide actionable insights from the actual study data
- Reference specific studies by title when relevant
- Be brief unless detailed analysis is specifically requested

Remember: You're helping advance {cancer_display} research by providing focused, data-driven insights from the available studies."""

    async def _search_relevant_studies(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for relevant studies using vector similarity"""
        try:
            if not self.vector_store:
                self.logger.warning("Vector store not available for search")
                return []
            
            # Enhance query for better medical context based on research domain
            cancer_display = {
                'prostate': 'Prostate cancer',
                'multiple_myeloma': 'Multiple myeloma',
                'breast': 'Breast cancer',
                'lung': 'Lung cancer',
                'colorectal': 'Colorectal cancer'
            }.get(self.research_domain, self.research_domain.replace('_', ' '))
            
            # Don't add prefix for author/institution queries
            query_lower = query.lower()
            if any(term in query_lower for term in ['author', 'wrote', 'institution', 'university', 'who wrote']):
                enhanced_query = query  # Use original query for author searches
            else:
                enhanced_query = f"{cancer_display} clinical study: {query}"
            
            # Add cancer type to filters if not already present
            if filters is None:
                filters = {}
            if 'cancer_type' not in filters:
                filters['cancer_type'] = self.research_domain
            
            # Search with filters
            search_results = await self.vector_store.search_abstracts(
                query=enhanced_query,
                filters=filters,
                top_k=15  # Increased to get more diverse results
            )
            
            self.logger.info(f"Vector search returned {len(search_results)} results for query: {query}")
            self.logger.info(f"Enhanced query: {enhanced_query}")
            self.logger.info(f"Filters used: {filters}")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Error searching studies: {e}")
            return []
    
    def _extract_search_filters(self, user_message: str) -> Dict[str, Any]:
        """Extract search filters from user message"""
        filters = {}
        message_lower = user_message.lower()
        
        # Study type filters
        if any(term in message_lower for term in ['phase 1', 'phase i']):
            filters['study_type'] = 'Phase 1'
        elif any(term in message_lower for term in ['phase 2', 'phase ii']):
            filters['study_type'] = 'Phase 2'
        elif any(term in message_lower for term in ['phase 3', 'phase iii']):
            filters['study_type'] = 'Phase 3'
        
        # MM subtype filters
        mm_subtypes = []
        if 'rrmm' in message_lower or 'relapsed' in message_lower or 'refractory' in message_lower:
            mm_subtypes.append('Relapsed/Refractory Multiple Myeloma')
        if 'ndmm' in message_lower or 'newly diagnosed' in message_lower:
            mm_subtypes.append('Newly Diagnosed Multiple Myeloma')
        if 'smoldering' in message_lower:
            mm_subtypes.append('Smoldering Multiple Myeloma')
        
        if mm_subtypes:
            filters['mm_subtype'] = mm_subtypes
        
        # Treatment type filters
        treatment_types = []
        if any(term in message_lower for term in ['car-t', 'cart', 'ciltacabtagene', 'idecabtagene']):
            treatment_types.extend(['CAR-T', 'ciltacabtagene', 'idecabtagene'])
        if any(term in message_lower for term in ['bispecific', 'teclistamab', 'talquetamab']):
            treatment_types.extend(['bispecific', 'teclistamab', 'talquetamab'])
        if any(term in message_lower for term in ['daratumumab', 'anti-cd38']):
            treatment_types.extend(['daratumumab', 'anti-CD38'])
        if any(term in message_lower for term in ['belantamab', 'adc']):
            treatment_types.extend(['belantamab', 'ADC'])
        
        if treatment_types:
            filters['treatment_type'] = treatment_types
        
        # Quality filter
        if 'high quality' in message_lower or 'reliable' in message_lower:
            filters['min_confidence'] = 0.8
        
        return filters
    
    def _format_study_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results as context for LLM"""
        if not search_results:
            return "No relevant studies found in the database."
        
        context = "**Relevant Clinical Studies:**\n\n"
        
        for i, study in enumerate(search_results, 1):
            study_info = study.get('study_info', {})
            metadata = study.get('metadata', {})
            
            # Get the text content which contains the actual abstract text
            text_content = metadata.get('text_content', '')
            
            context += f"**Study {i}: {study_info.get('title', metadata.get('study_title', 'Unknown Study'))}**\n"
            
            # If this is an author chunk or contains author info, include it prominently
            if 'author' in text_content.lower():
                # Extract author info from text
                lines = text_content.split('\n')
                for line in lines:
                    if 'author' in line.lower():
                        context += f"- {line.strip()}\n"
                        break
            
            # Include abstract number if available
            if metadata.get('abstract_id'):
                context += f"- Abstract Number: {metadata['abstract_id']}\n"
            
            if study_info.get('acronym'):
                context += f"- Acronym: {study_info['acronym']}\n"
            if study_info.get('nct_number'):
                context += f"- NCT: {study_info['nct_number']}\n"
            context += f"- Type: {study_info.get('study_type', 'Unknown')}\n"
            
            # Include relevant population info (cancer-specific)
            if metadata.get('mm_subtype'):
                mm_subtypes = metadata['mm_subtype']
                if isinstance(mm_subtypes, list) and mm_subtypes:
                    context += f"- Subtype/Population: {', '.join(mm_subtypes)}\n"
                elif mm_subtypes:
                    context += f"- Subtype/Population: {mm_subtypes}\n"
            
            # Include enrollment information if available
            if metadata.get('enrollment'):
                context += f"- Enrollment: {metadata['enrollment']} patients\n"
            
            if metadata.get('treatment_regimens'):
                treatments = metadata['treatment_regimens']
                if isinstance(treatments, list):
                    context += f"- Treatments: {', '.join(treatments)}\n"
                else:
                    context += f"- Treatments: {treatments}\n"
            
            if metadata.get('orr_value'):
                context += f"- ORR: {metadata['orr_value']}%\n"
            if metadata.get('pfs_median'):
                context += f"- PFS: {metadata['pfs_median']} months\n"
            if metadata.get('enrollment'):
                context += f"- Enrollment: {metadata['enrollment']} patients\n"
            
            context += f"- Relevance Score: {study['score']:.3f}\n"
            
            if study.get('content_preview'):
                context += f"- Context: {study['content_preview']}\n"
            
            context += "\n"
        
        return context
    
    def _determine_query_type(self, user_message: str) -> str:
        """Determine the type of query to provide appropriate response"""
        message_lower = user_message.lower()
        
        if any(term in message_lower for term in ['compare', 'vs', 'versus', 'difference']):
            return "comparison"
        elif any(term in message_lower for term in ['recommend', 'suggest', 'what should', 'best']):
            return "recommendation"
        elif any(term in message_lower for term in ['safety', 'adverse', 'toxicity', 'tolerability']):
            return "safety"
        elif any(term in message_lower for term in ['efficacy', 'response', 'survival', 'orr', 'pfs']):
            return "efficacy"
        elif any(term in message_lower for term in ['mechanism', 'how does', 'mode of action']):
            return "mechanism"
        elif any(term in message_lower for term in ['patient', 'selection', 'eligibility', 'criteria']):
            return "patient_selection"
        elif any(term in message_lower for term in ['market', 'competitive', 'landscape', 'commercial']):
            return "market_intelligence"
        elif any(term in message_lower for term in ['protocol', 'design', 'trial', 'study design']):
            return "protocol_design"
        else:
            return "general_inquiry"
    
    async def _generate_response(self, user_message: str, context: str, query_type: str) -> str:
        """Generate response using the selected LLM provider"""
        try:
            # Prepare the prompt
            conversation_context = self.conversation_memory.get_context_summary()
            
            prompt = f"""
{self.system_prompt}

**Current Query Type:** {query_type}
**Conversation Context:** {conversation_context}
**Relevant Studies:** {context}

**User Question:** {user_message}

Please provide a comprehensive, evidence-based response that:
1. Directly answers the user's question
2. References specific studies when relevant
3. Highlights key clinical insights
4. Maintains scientific accuracy
5. Uses clear, professional language
"""

            # Generate response based on selected provider
            if self.llm_provider == "claude" and "claude" in self.clients:
                return await self._generate_claude_response(prompt)
            elif self.llm_provider == "openai" and "openai" in self.clients:
                return await self._generate_openai_response(prompt)
            elif self.llm_provider == "gemini" and "gemini" in self.clients:
                return await self._generate_gemini_response(prompt)
            else:
                # Fallback to any available provider
                available_providers = list(self.clients.keys())
                if available_providers:
                    fallback_provider = available_providers[0]
                    self.logger.warning(f"Using fallback provider: {fallback_provider}")
                    if fallback_provider == "claude":
                        return await self._generate_claude_response(prompt)
                    elif fallback_provider == "openai":
                        return await self._generate_openai_response(prompt)
                    elif fallback_provider == "gemini":
                        return await self._generate_gemini_response(prompt)
                
                raise Exception("No LLM providers available")
                
        except Exception as e:
            self.logger.error(f"Error generating response with {self.llm_provider}: {e}")
            return f"I apologize, but I encountered an error processing your request with {self.llm_provider}. Please try again or contact support if the issue persists."
    
    async def _generate_claude_response(self, prompt: str) -> str:
        """Generate response using Claude"""
        try:
            response = await asyncio.to_thread(
                self.clients['claude'].messages.create,
                model=settings.CLAUDE_MODEL,
                max_tokens=2000,
                temperature=settings.TEMPERATURE,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise e
    
    async def _generate_openai_response(self, prompt: str) -> str:
        """Generate response using OpenAI"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                self.clients['openai'].chat.completions.create,
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=2000,
                temperature=settings.TEMPERATURE
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise e
    
    async def _generate_gemini_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            # Combine system prompt with user prompt for Gemini
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            
            response = await asyncio.to_thread(
                self.clients['gemini'].generate_content,
                full_prompt
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            raise e
    
    async def chat(self, user_message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Main chat interface with improved error handling and debugging"""
        try:
            # Update user context
            if user_context:
                self.conversation_memory.user_context.update(user_context)
            
            # Get session statistics for debugging
            vector_stats = self.vector_store.get_statistics()
            self.logger.info(f"Vector store stats: {vector_stats}")
            
            # Determine query type
            query_type = self._determine_query_type(user_message)
            
            # Extract search filters
            search_filters = self._extract_search_filters(user_message)
            
            # Search for relevant studies
            search_results = await self._search_relevant_studies(user_message, search_filters)
            self.logger.info(f"Search returned {len(search_results)} results")
            
            # Handle case where no studies are found - provide helpful response
            if not search_results:
                # Check if we have any data in the session at all
                total_studies = vector_stats.get('unique_studies', 0)
                
                if total_studies == 0:
                    helpful_response = """I don't have any clinical studies in your current session to analyze. 

**To get started:**
1. 📄 Go to the "Abstract Analysis" page
2. Upload or paste clinical abstracts 
3. Click "Generate Analysis" to process and embed them
4. Return here to ask questions about your data

**Example questions I can answer once you have data:**
- "What are the main treatments mentioned in my studies?"
- "Compare the efficacy results across studies"
- "What safety concerns should I be aware of?"
- "Which study had the best response rate?"

Would you like me to help you get started with uploading some data?"""
                else:
                    helpful_response = f"""I found {total_studies} studies in your session, but none matched your specific question: "{user_message}"

**Possible reasons:**
- Your question might be too specific for the available data
- Try asking broader questions like "What studies do I have?" or "Summarize my data"
- The studies might not contain information relevant to your query

**Try asking:**
- "What abstracts have I uploaded?"
- "Summarize the treatments in my studies"
- "What are the study types in my data?"
- "Show me the efficacy results"

Would you like me to provide a general overview of your uploaded studies instead?"""
                
                return {
                    "response": helpful_response,
                    "query_type": query_type,
                    "studies_referenced": 0,
                    "search_results": [],
                    "session_studies": total_studies,
                    "context_summary": "No relevant studies found",
                    "conversation_length": len(self.conversation_memory.messages),
                    "timestamp": datetime.now().isoformat(),
                    "debug_info": {
                        "vector_stats": vector_stats,
                        "search_filters": search_filters
                    }
                }
            
            # Format context
            context = self._format_study_context(search_results)
            
            # Generate response
            assistant_response = await self._generate_response(user_message, context, query_type)
            
            # Store conversation
            self.conversation_memory.add_message(
                role="user", 
                content=user_message, 
                context_used=[result['study_info']['title'] for result in search_results],
                search_results=search_results
            )
            
            self.conversation_memory.add_message(
                role="assistant", 
                content=assistant_response, 
                context_used=[result['study_info']['title'] for result in search_results],
                search_results=search_results,
                llm_provider=self.llm_provider  # Track which LLM was used
            )
            
            # Return comprehensive response
            return {
                "response": assistant_response,
                "query_type": query_type,
                "studies_referenced": len(search_results),
                "search_results": search_results,
                "context_summary": self.conversation_memory.get_context_summary(),
                "conversation_length": len(self.conversation_memory.messages),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            
            # Provide more helpful error response based on the error type
            if "api" in str(e).lower() or "key" in str(e).lower():
                error_response = """I'm experiencing an API connectivity issue. This might be due to:

**Possible solutions:**
1. **API Key Issue**: Check if your Anthropic/OpenAI API keys are properly configured
2. **Rate Limits**: You might have exceeded API rate limits - please wait a moment
3. **Network Issue**: Check your internet connection

**To configure API keys:**
- Add them to your Streamlit secrets or environment variables
- Ensure the keys have sufficient credits/quota

Please try again in a moment, or contact support if the issue persists."""
            
            elif "vector" in str(e).lower() or "pinecone" in str(e).lower():
                error_response = """I'm having trouble accessing the knowledge base. This might be due to:

**Possible solutions:**
1. **Pinecone Connection**: Check your vector database configuration
2. **Session Data**: Your session might have expired - try uploading data again
3. **Embedding Service**: The text embedding service might be temporarily unavailable

Please try uploading your abstracts again or refresh the page."""
            
            else:
                error_response = f"""I encountered a technical error while processing your request. 

**Error details:** {str(e)}

**Suggestions:**
1. Try rephrasing your question in simpler terms
2. Make sure you have uploaded some clinical abstracts first
3. If the problem persists, try refreshing the page

**Example questions that work well:**
- "What studies do I have?"
- "Compare the treatments"
- "Show me efficacy results"

Would you like to try a different question?"""
            
            return {
                "response": error_response,
                "error": str(e),
                "error_type": "technical_error",
                "timestamp": datetime.now().isoformat(),
                "debug_info": {
                    "session_id": getattr(self.vector_store, 'session_id', 'unknown'),
                    "vector_store_available": self.vector_store is not None
                }
            }
    
    async def get_study_insights(self, study_identifiers: List[str]) -> Dict[str, Any]:
        """Get detailed insights for specific studies"""
        try:
            # Get full study context
            study_contexts = await self.vector_store.get_study_context(study_identifiers)
            
            if not study_contexts:
                return {"error": "No studies found with the provided identifiers"}
            
            # Generate insights for each study
            insights = {}
            for study_context in study_contexts:
                study_info = study_context['study_info']
                study_title = study_info['title']
                
                # Create detailed analysis prompt
                chunks_text = "\n".join([
                    f"**{chunk_type}:** {content}"
                    for chunk_type, content in study_context['chunks'].items()
                ])
                
                prompt = f"""Analyze this clinical study and provide detailed insights:

**Study:** {study_title}

**Study Data:**
{chunks_text}

Please provide:
1. **Executive Summary** (key findings in 2-3 sentences)
2. **Clinical Significance** (importance for MM treatment)
3. **Efficacy Highlights** (key efficacy outcomes)
4. **Safety Profile** (notable safety considerations)
5. **Patient Population** (characteristics and selection)
6. **Competitive Positioning** (how it compares to other treatments)
7. **Strategic Implications** (for drug development/clinical practice)

Be specific and evidence-based."""

                # Generate insights
                response = await asyncio.to_thread(
                    self.clients[self.llm_provider].messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                insights[study_title] = {
                    "analysis": response.content[0].text,
                    "study_info": study_info,
                    "data_available": list(study_context['chunks'].keys())
                }
            
            return {
                "insights": insights,
                "total_studies": len(insights),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting study insights: {e}")
            return {"error": str(e)}
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            "total_messages": len(self.conversation_memory.messages),
            "conversation_started": self.conversation_memory.messages[0].timestamp.isoformat() if self.conversation_memory.messages else None,
            "last_activity": self.conversation_memory.messages[-1].timestamp.isoformat() if self.conversation_memory.messages else None,
            "topics_discussed": self.conversation_memory.get_context_summary(),
            "user_context": self.conversation_memory.user_context,
            "capabilities": self.capabilities
        }
    
    def reset_conversation(self):
        """Reset conversation memory"""
        self.conversation_memory = ConversationMemory()
    
    async def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return self.vector_store.get_statistics() 