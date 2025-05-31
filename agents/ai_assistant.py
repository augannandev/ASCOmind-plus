# agents/ai_assistant.py - ADVANCED AI RESEARCH ASSISTANT

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

import anthropic
import openai
from pydantic import BaseModel

from agents.vector_store import IntelligentVectorStore
from config.settings import settings

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    context_used: Optional[List[str]] = None
    search_results: Optional[List[Dict]] = None

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_messages: int = 20):
        self.messages: List[ConversationMessage] = []
        self.max_messages = max_messages
        self.session_id = None
        self.user_context = {}  # Store user preferences, current studies, etc.
    
    def add_message(self, role: str, content: str, context_used: Optional[List[str]] = None, 
                   search_results: Optional[List[Dict]] = None):
        """Add message to conversation history"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            context_used=context_used,
            search_results=search_results
        )
        
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_context_summary(self) -> str:
        """Get a summary of the conversation context"""
        if not self.messages:
            return "New conversation about multiple myeloma research."
        
        recent_topics = []
        for msg in self.messages[-5:]:  # Last 5 messages
            if msg.role == 'user' and len(msg.content) > 20:
                recent_topics.append(msg.content[:100])
        
        return f"Recent discussion topics: {'; '.join(recent_topics)}"
    
    def get_formatted_history(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM (excluding system messages)"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages[-10:]  # Last 10 messages for context
            if msg.role in ["user", "assistant"]  # Exclude system messages
        ]

class AdvancedAIAssistant:
    """Intelligent AI assistant for multiple myeloma research"""
    
    def __init__(self, vector_store: Optional[IntelligentVectorStore] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM clients
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Vector store for knowledge retrieval (session-isolated)
        if vector_store:
            self.vector_store = vector_store
            self.logger.info(f"AI Assistant using provided vector store with session: {vector_store.get_session_id()}")
        else:
            # Fallback: create own vector store (should be avoided in production)
            self.vector_store = IntelligentVectorStore()
            self.logger.warning("AI Assistant created its own vector store - session isolation may be compromised")
        
        # Conversation memory
        self.conversation_memory = ConversationMemory()
        
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
    
    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for the assistant"""
        return """You are Dr. ASCOmind+, an advanced AI research assistant specializing in multiple myeloma clinical research and drug development. You have access to a curated database of clinical studies and research data.

**Your Expertise:**
- Multiple myeloma pathophysiology and treatment mechanisms
- Clinical trial design and regulatory requirements
- Competitive landscape analysis and market intelligence
- Treatment sequencing and patient selection strategies
- Safety profiling and risk-benefit analysis
- Biomarker strategies and precision medicine approaches

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
- Professional but approachable
- Use medical terminology appropriately
- Provide clear executive summaries
- Offer multiple perspectives when relevant
- Ask clarifying questions when needed

Remember: You're helping advance multiple myeloma research and improve patient outcomes through intelligent analysis and strategic insights."""

    async def _search_relevant_studies(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for relevant studies using vector similarity"""
        try:
            # Enhance query for better medical context
            enhanced_query = f"Multiple myeloma clinical study: {query}"
            
            # Search with filters
            search_results = await self.vector_store.search_abstracts(
                query=enhanced_query,
                filters=filters,
                top_k=5
            )
            
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
            context += f"**Study {i}: {study['study_title']}**\n"
            if study.get('study_acronym'):
                context += f"- Acronym: {study['study_acronym']}\n"
            if study.get('nct_number'):
                context += f"- NCT: {study['nct_number']}\n"
            context += f"- Type: {study['study_type']}\n"
            
            if study.get('mm_subtype'):
                context += f"- Population: {', '.join(study['mm_subtype'])}\n"
            
            if study.get('treatment_regimens'):
                context += f"- Treatments: {', '.join(study['treatment_regimens'])}\n"
            
            if study.get('orr_value'):
                context += f"- ORR: {study['orr_value']}%\n"
            if study.get('pfs_median'):
                context += f"- PFS: {study['pfs_median']} months\n"
            if study.get('enrollment'):
                context += f"- Enrollment: {study['enrollment']} patients\n"
            
            context += f"- Relevance Score: {study['score']:.3f}\n"
            
            if study.get('text_preview'):
                context += f"- Context: {study['text_preview']}\n"
            
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
        """Generate response using Claude with context"""
        try:
            # Create query-specific prompts
            query_prompts = {
                "comparison": "Provide a detailed comparison including efficacy, safety, patient populations, and strategic implications. Use tables or structured format when helpful.",
                "recommendation": "Provide evidence-based recommendations with clear rationale. Consider efficacy, safety, patient factors, and practical considerations.",
                "safety": "Focus on safety profiles, adverse events, management strategies, and risk-benefit considerations.",
                "efficacy": "Analyze efficacy endpoints in detail. Discuss response rates, survival outcomes, and clinical significance.",
                "mechanism": "Explain mechanisms of action, target pathways, and therapeutic rationale.",
                "patient_selection": "Discuss patient selection criteria, biomarkers, and optimization strategies.",
                "market_intelligence": "Provide competitive landscape analysis and strategic positioning insights.",
                "protocol_design": "Offer protocol design recommendations including endpoints, patient selection, and regulatory considerations.",
                "general_inquiry": "Provide a comprehensive analysis addressing all relevant aspects of the question."
            }
            
            specific_prompt = query_prompts.get(query_type, query_prompts["general_inquiry"])
            
            # Get conversation history
            conversation_history = self.conversation_memory.get_formatted_history()
            
            # Construct messages for Claude
            messages = [
                *conversation_history,
                {
                    "role": "user", 
                    "content": f"""**User Question:** {user_message}

**Available Clinical Data:**
{context}

**Response Instructions:** {specific_prompt}

Please provide a comprehensive, evidence-based response that addresses the user's question using the available clinical data. Structure your response clearly and provide actionable insights."""
                }
            ]
            
            # Generate response with Claude using system parameter
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                system=self.system_prompt,  # Use system parameter instead of message
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            # Fallback to OpenAI if Claude fails
            try:
                messages_openai = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Question: {user_message}\n\nContext: {context}\n\nPlease provide a helpful response."}
                ]
                
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4-turbo-preview",
                    messages=messages_openai,
                    max_tokens=1500,
                    temperature=0.3
                )
                
                return response.choices[0].message.content
                
            except Exception as e2:
                self.logger.error(f"Both Claude and OpenAI failed: {e2}")
                return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    async def chat(self, user_message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Main chat interface"""
        try:
            # Update user context
            if user_context:
                self.conversation_memory.user_context.update(user_context)
            
            # Determine query type
            query_type = self._determine_query_type(user_message)
            
            # Extract search filters
            search_filters = self._extract_search_filters(user_message)
            
            # Search for relevant studies
            search_results = await self._search_relevant_studies(user_message, search_filters)
            
            # Format context
            context = self._format_study_context(search_results)
            
            # Generate response
            assistant_response = await self._generate_response(user_message, context, query_type)
            
            # Update conversation memory
            self.conversation_memory.add_message(
                role="user", 
                content=user_message
            )
            self.conversation_memory.add_message(
                role="assistant", 
                content=assistant_response,
                context_used=[result['study_title'] for result in search_results],
                search_results=search_results
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
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try rephrasing your question.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
                    self.anthropic_client.messages.create,
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