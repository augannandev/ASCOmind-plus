#!/usr/bin/env python3
"""
Test script for AI Assistant and Vector Store functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Test if configuration and secrets are loaded properly"""
    print("🔧 Testing configuration...")
    
    try:
        from config.settings import settings
        
        # Refresh settings to load from secrets
        settings.refresh_from_secrets()
        
        print(f"✅ Settings loaded successfully")
        print(f"📊 Required keys available: {settings.has_required_keys()}")
        print(f"🤖 Anthropic API: {'✅ Configured' if settings.ANTHROPIC_API_KEY else '❌ Missing'}")
        print(f"🔮 OpenAI API: {'✅ Configured' if settings.OPENAI_API_KEY else '❌ Missing'}")
        print(f"🌲 Pinecone API: {'✅ Configured' if settings.PINECONE_API_KEY else '❌ Missing'}")
        print(f"📝 Pinecone Index: {settings.PINECONE_INDEX_NAME}")
        
        return settings.has_required_keys()
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_vector_store():
    """Test vector store initialization"""
    print("\n🧠 Testing Vector Store...")
    
    try:
        from agents.vector_store import IntelligentVectorStore
        
        vector_store = IntelligentVectorStore()
        stats = vector_store.get_statistics()
        
        print(f"✅ Vector store initialized successfully")
        print(f"📈 Vector store stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_ai_assistant():
    """Test AI assistant initialization"""
    print("\n🤖 Testing AI Assistant...")
    
    try:
        from agents.ai_assistant import AdvancedAIAssistant
        
        ai_assistant = AdvancedAIAssistant()
        summary = ai_assistant.get_conversation_summary()
        
        print(f"✅ AI assistant initialized successfully")
        print(f"🎯 Capabilities: {len(ai_assistant.capabilities)} available")
        print(f"💬 Conversation summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI assistant test failed: {e}")
        return False

def test_full_integration():
    """Test full integration"""
    print("\n🚀 Testing Full Integration...")
    
    try:
        # Test imports
        from main import ASCOmindApp
        
        print("✅ All imports successful")
        print("✅ ASCOmindApp can be imported")
        print("🎉 Full integration test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ASCOmind+ AI Assistant Test Suite")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_vector_store,
        test_ai_assistant,
        test_full_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    test_names = ["Configuration", "Vector Store", "AI Assistant", "Full Integration"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    success_rate = sum(results) / len(results)
    print(f"\n🎯 Overall Success Rate: {success_rate:.1%}")
    
    if success_rate == 1.0:
        print("🎉 All tests passed! Your AI Assistant is ready to use!")
    elif success_rate >= 0.5:
        print("⚠️  Some tests failed. Check your API configuration.")
    else:
        print("❌ Multiple test failures. Please check your setup.")
    
    return success_rate == 1.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 