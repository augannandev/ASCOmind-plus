#!/usr/bin/env python3
# demo_cancer_first.py - DEMONSTRATION OF NEW CANCER-FIRST UI

"""
Demonstration script for the new Cancer-First UI implementation.
This script shows how the new system works and can be used for testing.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

from config.cancer_types import CancerType, get_all_cancer_types, get_cancer_type_config
from agents.cache_manager import CancerSpecificCacheManager
from agents.vector_store import IntelligentVectorStore


async def demo_cancer_types():
    """Demonstrate cancer type configurations"""
    print("🧬 ASCOmind+ Cancer-First UI Demo")
    print("=" * 50)
    
    print("\n1. Available Cancer Types:")
    print("-" * 30)
    
    cancer_types = get_all_cancer_types()
    for i, config in enumerate(cancer_types, 1):
        print(f"{i:2d}. {config.icon} {config.display_name}")
        print(f"    {config.description}")
        print(f"    Specializations: {', '.join(config.specializations[:3])}...")
        print(f"    Key Endpoints: {len(config.key_endpoints)} endpoints")
        print(f"    Treatments: {len(config.typical_treatments)} types")
        print()


async def demo_cache_manager():
    """Demonstrate cache management functionality"""
    print("\n2. Cache Management System:")
    print("-" * 30)
    
    cache_manager = CancerSpecificCacheManager()
    
    # Get cache status
    status = await cache_manager.get_cache_status()
    print(f"Cache directory: {status['cache_directory']}")
    print(f"Memory cache size: {status['memory_cache_size']} entries")
    
    print("\nCache status by cancer type:")
    for cancer_type, cache_status in status['cancer_types'].items():
        visualizations = "✅" if cache_status['visualizations_cached'] else "❌"
        summary = "✅" if cache_status['summary_cached'] else "❌"
        data = "✅" if cache_status['data_cached'] else "❌"
        
        print(f"  {cancer_type:20s} | Viz: {visualizations} | Summary: {summary} | Data: {data}")


async def demo_vector_store_filtering():
    """Demonstrate cancer-type filtering in vector store"""
    print("\n3. Vector Store Cancer Filtering:")
    print("-" * 30)
    
    # Create cancer-specific vector stores
    mm_store = IntelligentVectorStore(session_id="cancer_multiple_myeloma_demo")
    breast_store = IntelligentVectorStore(session_id="cancer_breast_cancer_demo")
    
    print(f"Multiple Myeloma store session: {mm_store.session_id}")
    print(f"Breast Cancer store session: {breast_store.session_id}")
    
    # Demonstrate search filtering
    print("\nDemo search filters:")
    
    # Multiple myeloma filter
    mm_filters = {
        'cancer_type': 'multiple_myeloma',
        'min_confidence': 0.8
    }
    print(f"MM filters: {mm_filters}")
    
    # Breast cancer filter
    breast_filters = {
        'cancer_type': 'breast_cancer',
        'study_type': 'Phase 3'
    }
    print(f"Breast cancer filters: {breast_filters}")


async def demo_new_ui_flow():
    """Demonstrate the new UI flow"""
    print("\n4. New UI Flow Demonstration:")
    print("-" * 30)
    
    print("Step 1: User visits ASCOmind+")
    print("   → Sees cancer type selection interface")
    print("   → Beautiful cards for each cancer type")
    print("   → No file upload required!")
    
    print("\nStep 2: User selects 'Multiple Myeloma'")
    print("   → System loads cached data instantly")
    print("   → Pre-generated visualizations appear")
    print("   → Cancer-specific dashboard shows metrics")
    
    print("\nStep 3: User explores analytics")
    print("   → Sees MM-specific insights")
    print("   → Views treatment landscape charts")
    print("   → Examines efficacy comparisons")
    
    print("\nStep 4: User asks questions to AI")
    print("   → AI only searches MM-related studies")
    print("   → Responses are focused and accurate")
    print("   → No irrelevant cancer data interferes")
    
    print("\nStep 5: User switches to Breast Cancer")
    print("   → One click to change cancer type")
    print("   → New cached data loads instantly")
    print("   → Completely different specialized interface")


async def demo_performance_benefits():
    """Demonstrate performance improvements"""
    print("\n5. Performance Benefits:")
    print("-" * 30)
    
    print("🚀 Old UI Flow:")
    print("   1. Upload files (slow)")
    print("   2. Extract metadata (slow)")
    print("   3. Generate visualizations (slow)")
    print("   4. Create embeddings (slow)")
    print("   5. Ready to use")
    print("   Total time: 2-5 minutes")
    
    print("\n⚡ New UI Flow:")
    print("   1. Select cancer type (instant)")
    print("   2. Load cached data (instant)")
    print("   3. Show visualizations (instant)")
    print("   4. AI ready to chat (instant)")
    print("   Total time: < 1 second")
    
    print("\n💡 Cache Pre-generation:")
    print("   - Runs in background")
    print("   - Updates daily/weekly")
    print("   - Smart invalidation")
    print("   - Memory + file caching")


async def demo_specialization_examples():
    """Show specialization examples for different cancers"""
    print("\n6. Cancer-Specific Specializations:")
    print("-" * 30)
    
    examples = [
        (CancerType.MULTIPLE_MYELOMA, "NDMM vs RRMM treatment landscapes"),
        (CancerType.BREAST_CANCER, "Triple-negative vs HER2+ targeted therapies"),
        (CancerType.LUNG_CANCER, "EGFR+ vs ALK+ precision medicine"),
        (CancerType.MELANOMA, "BRAF mutant vs wild-type immunotherapy"),
    ]
    
    for cancer_type, example in examples:
        config = get_cancer_type_config(cancer_type)
        print(f"{config.icon} {config.display_name}:")
        print(f"   Example: {example}")
        print(f"   Specializations: {', '.join(config.specializations)}")
        print(f"   Key endpoints: {', '.join(config.key_endpoints[:2])}...")
        print()


async def demo_ai_assistant_improvements():
    """Demonstrate AI assistant improvements"""
    print("\n7. AI Assistant Improvements:")
    print("-" * 30)
    
    print("🤖 Old AI Assistant:")
    print("   - Searches all cancer types")
    print("   - May return irrelevant results")
    print("   - Generic responses")
    print("   - Confusion between cancer types")
    
    print("\n🎯 New AI Assistant:")
    print("   - Cancer-type specific knowledge")
    print("   - Filtered vector search")
    print("   - Specialized system prompts")
    print("   - Focused, accurate responses")
    
    print("\nExample Questions:")
    print("Multiple Myeloma AI:")
    print("   'What are the latest CAR-T therapies for MM?'")
    print("   → Only searches MM studies")
    print("   → Knows MM-specific terminology")
    print("   → Understands NDMM vs RRMM context")
    
    print("\nBreast Cancer AI:")
    print("   'Compare CDK4/6 inhibitors in HR+ disease'")
    print("   → Only searches breast cancer studies")
    print("   → Understands receptor subtypes")
    print("   → Focuses on relevant endpoints")


def create_sample_config():
    """Create sample configuration for demo"""
    print("\n8. Sample Configuration:")
    print("-" * 30)
    
    mm_config = get_cancer_type_config(CancerType.MULTIPLE_MYELOMA)
    
    config_dict = {
        "cancer_type": mm_config.id,
        "display_name": mm_config.display_name,
        "description": mm_config.description,
        "specializations": mm_config.specializations,
        "key_endpoints": mm_config.key_endpoints,
        "ui_theme": {
            "primary_color": mm_config.color_primary,
            "secondary_color": mm_config.color_secondary,
            "icon": mm_config.icon
        }
    }
    
    print("Sample Multiple Myeloma configuration:")
    print(json.dumps(config_dict, indent=2))


async def main():
    """Run the complete demonstration"""
    print("Starting ASCOmind+ Cancer-First UI Demo...")
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await demo_cancer_types()
    await demo_cache_manager()
    await demo_vector_store_filtering()
    await demo_new_ui_flow()
    await demo_performance_benefits()
    await demo_specialization_examples()
    await demo_ai_assistant_improvements()
    create_sample_config()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nTo run the new UI:")
    print("   streamlit run main_cancer_first.py")
    print("\nTo run the old UI:")
    print("   streamlit run main.py")
    print("\nBoth can run simultaneously on different ports.")


if __name__ == "__main__":
    asyncio.run(main())
