#!/usr/bin/env python3
"""
Test Content Processing Pipeline

Quick test to validate that the content processing bots work together correctly.
"""

import json
from bots.content_processor_agent import ContentProcessorAgent

def test_content_processing():
    """Test the complete content processing pipeline"""
    
    print("🧪 Testing Content Processing Pipeline")
    print("=" * 50)
    
    # Sample universe data (like what UniverseBuilder produces)
    sample_universe_data = {
        "world_info": {
            "world_name": "Eldoria",
            "world_description": "Eldoria is a realm where magic flows through ancient ley lines, connecting three kingdoms under starlit skies. The land is steeped in both wonder and danger, where heroes rise to face the stirring darkness beneath the Crystal Mountains.",
            "theme_list": "magic, adventure, ancient evil, kingdoms",
            "natural_laws": "Magic is governed by ley lines that pulse with celestial energy."
        },
        "pantheon": {
            "structure": "The pantheon consists of six major deities who govern different aspects of existence.",
            "major_deities": [
                "Solara, Goddess of Sun and Light",
                "Lunaris, God of Moon and Time", 
                "Malakar, The Ancient Evil"
            ],
            "divine_influence": "The gods actively intervene in mortal affairs through signs and miracles."
        },
        "magic_system": {
            "commonality": "Magic is common, with most towns having a wizard or healer.",
            "mechanics": "Magic flows through ley lines and is channeled through ritual and focus.",
            "limitations": "Ley lines can become unstable, causing unpredictable magical surges."
        },
        "global_threats": [
            {
                "primary_threat": "The Awakening of Malakar",
                "threat_details": "Deep beneath the Crystal Mountains, the ancient evil Malakar stirs from millennia of slumber, threatening to corrupt the world.",
                "world_impact": "Crops wither, strange creatures emerge, and an aura of unease spreads across the land."
            }
        ]
    }
    
    # Test campaign ID
    test_campaign_id = "test-campaign-123"
    
    try:
        # Initialize content processor
        processor = ContentProcessorAgent(debug=True)
        
        print("\n🏗️ Processing sample universe content...")
        
        # Process the universe data
        processed_sections = processor.process_universe_content(test_campaign_id, sample_universe_data)
        
        print(f"\n✅ Processing complete! Generated {len(processed_sections)} sections")
        
        # Display results
        for section in processed_sections:
            print(f"\n📄 SECTION: {section['content_type']}")
            print(f"   Title: {section['title']}")
            print(f"   Tags: {section['tags'][:5]}{'...' if len(section['tags']) > 5 else ''}")
            print(f"   Entities: {len(section['entities'])}")
            print(f"   Chunks: {len(section['chunks'])}")
            
            # Show first entity
            if section['entities']:
                entity = section['entities'][0]
                print(f"   First Entity: {entity['entity_name']} ({entity['entity_type']})")
            
            # Show first chunk info
            if section['chunks']:
                chunk = section['chunks'][0]
                print(f"   First Chunk: {chunk['word_count']} words, topic: {chunk['topic']}")
        
        print("\n🎯 Content processing pipeline test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Content processing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_expansion_processing():
    """Test processing of expanded content"""
    
    print("\n🔄 Testing Expansion Content Processing")
    print("=" * 50)
    
    expanded_content = """
    Solara, the radiant goddess of sun and light, manifests her power through golden rays that pierce even the deepest darkness. Her clergy, led by High Priest Aldric at the Temple of Dawn, practices healing magic and conducts daily sunrise ceremonies. The temple itself sits atop Crystal Peak, where Solara's divine energy is strongest.
    
    The Church of Solara maintains a complex hierarchy of priests, healers, and paladins who serve throughout the three kingdoms. They are particularly active in fighting the corruption of Malakar, using blessed weapons and divine spells to purify tainted lands.
    """
    
    try:
        processor = ContentProcessorAgent(debug=True)
        
        # Process expansion content
        processed_expansion = processor.process_expansion_content(
            campaign_id="test-campaign-123",
            content_type="pantheon",
            expanded_content=expanded_content,
            parent_content_id="parent-uuid-123"
        )
        
        print(f"\n✅ Expansion processing complete!")
        print(f"   Tags: {processed_expansion['tags'][:8]}")
        print(f"   Entities: {len(processed_expansion['entities'])}")
        print(f"   Chunks: {len(processed_expansion['chunks'])}")
        
        # Show extracted entities
        for entity in processed_expansion['entities'][:3]:
            print(f"   Entity: {entity['entity_name']} ({entity['entity_type']})")
        
        print("\n🎯 Expansion processing test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Expansion processing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Content Processing Tests")
    
    # Test basic processing
    basic_test = test_content_processing()
    
    # Test expansion processing
    expansion_test = test_expansion_processing()
    
    print("\n" + "=" * 50)
    if basic_test and expansion_test:
        print("🎉 ALL TESTS PASSED! Content processing pipeline is ready!")
        print("\n💡 Next Steps:")
        print("   1. Integrate with your existing world builder")
        print("   2. Add database saving functionality")
        print("   3. Connect to vector embedding service")
        print("   4. Build expansion bots that use this pipeline")
    else:
        print("❌ Some tests failed. Check the error messages above.")
    
    print("\n🔧 To integrate with existing code:")
    print("   from bots.content_processor_agent import ContentProcessorAgent")
    print("   processor = ContentProcessorAgent()")
    print("   processed = processor.process_universe_content(campaign_id, universe_data)") 