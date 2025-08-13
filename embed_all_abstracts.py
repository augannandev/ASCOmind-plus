#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
from agents.cache_manager import CancerSpecificCacheManager
from agents.vector_store import IntelligentVectorStore
from agents.ai_assistant import AdvancedAIAssistant
import streamlit as st

async def embed_all_prostate_abstracts():
    """Embed all available prostate cancer abstracts to Pinecone"""
    
    print("🚀 Starting embedding process for all prostate cancer abstracts...")
    
    # Initialize components
    cache_manager = CancerSpecificCacheManager()
    
    # Load all cached prostate abstracts
    print("📥 Loading cached prostate cancer data...")
    cached_abstracts = await cache_manager.get_cached_data("prostate")
    
    if not cached_abstracts:
        print("❌ No cached prostate cancer data found!")
        print("💡 Please run the batch processor first to process the abstracts.")
        return
    
    print(f"✅ Found {len(cached_abstracts)} cached prostate cancer abstracts")
    
    # Initialize vector store with prostate session
    print("🔧 Initializing Pinecone vector store...")
    vector_store = IntelligentVectorStore(session_id="prostate_full_embed")
    
    # Check current status
    stats = vector_store.get_statistics()
    print(f"📊 Current Pinecone status: {stats['total_vectors']} vectors")
    
    # Embed all abstracts
    print(f"🔄 Embedding {len(cached_abstracts)} abstracts to Pinecone...")
    try:
        embedding_results = await vector_store.batch_embed_abstracts(cached_abstracts)
        success_count = embedding_results.get('success', 0)
        
        print(f"✅ Successfully embedded {success_count} of {len(cached_abstracts)} abstracts!")
        
        # Verify final status
        final_stats = vector_store.get_statistics()
        print(f"📊 Final Pinecone status: {final_stats['total_vectors']} vectors")
        
        # Initialize AI Assistant for testing
        print("🤖 Testing AI Assistant with new embeddings...")
        ai_assistant = AdvancedAIAssistant(
            vector_store=vector_store,
            llm_provider="gemini"
        )
        ai_assistant.research_domain = "prostate"
        
        # Test query
        test_result = await ai_assistant.chat("How many abstracts are embedded?")
        print(f"🧪 Test query result: {test_result.get('response', 'No response')[:200]}...")
        
        return success_count
        
    except Exception as e:
        print(f"❌ Error during embedding: {e}")
        return 0

if __name__ == "__main__":
    # Run the embedding process
    embedded_count = asyncio.run(embed_all_prostate_abstracts())
    
    if embedded_count > 0:
        print(f"\n🎉 Embedding complete! {embedded_count} abstracts are now available in Pinecone.")
        print("🔄 Please refresh your Streamlit app to see the updated data.")
    else:
        print("\n❌ Embedding failed. Please check the error messages above.")
