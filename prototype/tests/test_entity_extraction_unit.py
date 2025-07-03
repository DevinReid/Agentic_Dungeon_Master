#!/usr/bin/env python3
"""
Unit Test for Entity Extraction

Focused test to validate entity extraction with known input and expected output.
Uses the existing test data with clearly defined expected entities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import json
from bots.entity_extractor_agent import EntityExtractorAgent

def test_pantheon_entity_extraction():
    """Test entity extraction from pantheon content"""
    
    print("🧪 TESTING PANTHEON ENTITY EXTRACTION")
    print("=" * 50)
    
    # Sample pantheon content from our test data
    pantheon_content = """
    The pantheon of Eldoria is a diverse tapestry of deities, each ruling over distinct domains and embodying the myriad aspects of existence. Temples and shrines dedicated to these gods dot the landscape, serving as centers of worship and pilgrimage.
    
    The major deities include:
    - Solara, Goddess of the Sun and Light
    - Lunaris, God of the Moon and Time  
    - Terran, God of Earth and Nature
    - Aqualis, Goddess of Water and Healing
    - Zephyr, God of Wind and Freedom
    - Ignis, Goddess of Fire and Passion
    
    The gods of Eldoria are active and frequently intervene in mortal affairs, manifesting omens and performing miracles to guide or challenge their followers.
    """
    
    # Expected entities to be extracted
    expected_entities = {
        'deities': [
            'Solara', 'Lunaris', 'Terran', 'Aqualis', 'Zephyr', 'Ignis'
        ],
        'locations': [
            'Eldoria'  # Should extract the world name
        ]
    }
    
    test_campaign_id = str(uuid.uuid4())
    existing_tags = ["pantheon", "deities", "gods", "divine"]
    
    try:
        print(f"📋 Test Campaign ID: {test_campaign_id}")
        print(f"📖 Content length: {len(pantheon_content.split())} words")
        print(f"🎯 Expected deities: {len(expected_entities['deities'])}")
        print(f"🎯 Expected locations: {len(expected_entities['locations'])}")
        
        # Test entity extraction
        extractor = EntityExtractorAgent(debug=True)
        extracted_entities = extractor.extract_entities(
            content=pantheon_content,
            content_type="pantheon",
            existing_tags=existing_tags,
            campaign_id=test_campaign_id
        )
        
        print(f"\n✅ Extraction complete!")
        print(f"📊 Extracted entity types: {list(extracted_entities.keys())}")
        
        # Validate results
        found_deities = []
        found_locations = []
        
        for entity_type, entities in extracted_entities.items():
            print(f"   • {entity_type}: {len(entities)} entities")
            
            for entity in entities:
                entity_name = entity.get('name', entity.get('entity_name', 'Unknown'))
                print(f"     - {entity_name}")
                
                if entity_type == 'deities':
                    found_deities.append(entity_name)
                elif entity_type == 'locations':
                    found_locations.append(entity_name)
        
        # Check against expected entities
        print(f"\n🔍 VALIDATION RESULTS:")
        
        # Check deities
        deity_matches = 0
        for expected_deity in expected_entities['deities']:
            if any(expected_deity in found_deity for found_deity in found_deities):
                deity_matches += 1
                print(f"   ✅ Found deity: {expected_deity}")
            else:
                print(f"   ❌ Missing deity: {expected_deity}")
        
        # Check locations  
        location_matches = 0
        for expected_location in expected_entities['locations']:
            if any(expected_location in found_location for found_location in found_locations):
                location_matches += 1
                print(f"   ✅ Found location: {expected_location}")
            else:
                print(f"   ❌ Missing location: {expected_location}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Deities found: {deity_matches}/{len(expected_entities['deities'])}")
        print(f"   Locations found: {location_matches}/{len(expected_entities['locations'])}")
        
        success = (deity_matches >= 4 and location_matches >= 1)  # Allow some flexibility
        
        if success:
            print(f"✅ Pantheon entity extraction test PASSED!")
        else:
            print(f"❌ Pantheon entity extraction test FAILED!")
            
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_global_threats_entity_extraction():
    """Test entity extraction from global threats content"""
    
    print("\n🧪 TESTING GLOBAL THREATS ENTITY EXTRACTION")
    print("=" * 50)
    
    # Global threats content from test data
    threats_content = """
    Deep beneath the Crystalline Mountains, the Dread Titan known as Malakar stirs from its millennia-long slumber. Heralded by earthquakes and violent storms, the Titan's awakening threatens to shatter the delicate balance of the world, unleashing an era of chaos and destruction.
    
    The presence of Malakar casts a shadow over daily life in Eldoria. Crops wither, strange creatures emerge from the shadows, and an air of unease permeates even the most vibrant of towns.
    
    A coalition of wizards, clerics, and warriors known as the Order of the Dawn has formed to counter the threat of Malakar, seeking ancient knowledge and relics capable of subduing the Titan.
    """
    
    # Expected entities
    expected_entities = {
        'threats': ['Malakar', 'Dread Titan'],
        'locations': ['Crystalline Mountains', 'Eldoria'],
        'organizations': ['Order of the Dawn']
    }
    
    test_campaign_id = str(uuid.uuid4())
    existing_tags = ["global_threats", "ancient_evil", "titan", "danger"]
    
    try:
        print(f"📋 Test Campaign ID: {test_campaign_id}")
        print(f"📖 Content length: {len(threats_content.split())} words")
        print(f"🎯 Expected threats: {len(expected_entities['threats'])}")
        print(f"🎯 Expected locations: {len(expected_entities['locations'])}")
        print(f"🎯 Expected organizations: {len(expected_entities['organizations'])}")
        
        # Test entity extraction
        extractor = EntityExtractorAgent(debug=True)
        extracted_entities = extractor.extract_entities(
            content=threats_content,
            content_type="global_threats",
            existing_tags=existing_tags,
            campaign_id=test_campaign_id
        )
        
        print(f"\n✅ Extraction complete!")
        print(f"📊 Extracted entity types: {list(extracted_entities.keys())}")
        
        # Validate results
        found_entities = {
            'threats': [],
            'locations': [],
            'organizations': []
        }
        
        for entity_type, entities in extracted_entities.items():
            print(f"   • {entity_type}: {len(entities)} entities")
            
            for entity in entities:
                entity_name = entity.get('name', entity.get('entity_name', 'Unknown'))
                print(f"     - {entity_name}")
                
                if entity_type in found_entities:
                    found_entities[entity_type].append(entity_name)
        
        # Check against expected entities
        print(f"\n🔍 VALIDATION RESULTS:")
        total_matches = 0
        total_expected = 0
        
        for entity_type, expected_list in expected_entities.items():
            matches = 0
            for expected_entity in expected_list:
                if any(expected_entity in found_entity for found_entity in found_entities[entity_type]):
                    matches += 1
                    print(f"   ✅ Found {entity_type}: {expected_entity}")
                else:
                    print(f"   ❌ Missing {entity_type}: {expected_entity}")
            
            print(f"   {entity_type.title()}: {matches}/{len(expected_list)}")
            total_matches += matches
            total_expected += len(expected_list)
        
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total entities found: {total_matches}/{total_expected}")
        print(f"   Success rate: {(total_matches/total_expected)*100:.1f}%")
        
        success = (total_matches >= total_expected * 0.6)  # 60% success rate threshold
        
        if success:
            print(f"✅ Global threats entity extraction test PASSED!")
        else:
            print(f"❌ Global threats entity extraction test FAILED!")
            
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_entity_extraction():
    """Test with very simple, clear content to debug basic extraction"""
    
    print("\n🧪 TESTING SIMPLE ENTITY EXTRACTION")
    print("=" * 50)
    
    # Very simple content
    simple_content = "The wizard Gandalf lives in the Tower of Magic in the city of Eldoria."
    
    expected_entities = {
        'npcs': ['Gandalf'],
        'locations': ['Tower of Magic', 'Eldoria']
    }
    
    test_campaign_id = str(uuid.uuid4())
    existing_tags = ["fantasy", "wizard"]
    
    try:
        print(f"📋 Simple content: {simple_content}")
        print(f"🎯 Expected NPCs: {expected_entities['npcs']}")
        print(f"🎯 Expected locations: {expected_entities['locations']}")
        
        extractor = EntityExtractorAgent(debug=True)
        extracted_entities = extractor.extract_entities(
            content=simple_content,
            content_type="test",
            existing_tags=existing_tags,
            campaign_id=test_campaign_id
        )
        
        print(f"\n✅ Extraction complete!")
        
        # Show all extracted entities
        total_extracted = 0
        for entity_type, entities in extracted_entities.items():
            if entities:
                print(f"   • {entity_type}: {len(entities)} entities")
                for entity in entities:
                    entity_name = entity.get('name', entity.get('entity_name', 'Unknown'))
                    print(f"     - {entity_name}")
                    total_extracted += 1
        
        if total_extracted > 0:
            print(f"✅ Simple entity extraction test PASSED! ({total_extracted} entities)")
            return True
        else:
            print(f"❌ Simple entity extraction test FAILED! (No entities extracted)")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Entity Extraction Unit Tests")
    print("Testing individual components with known input/output")
    print()
    
    # Run tests in order of complexity
    test1 = test_simple_entity_extraction()
    test2 = test_pantheon_entity_extraction()
    test3 = test_global_threats_entity_extraction()
    
    print("\n" + "=" * 60)
    
    if test1 and test2 and test3:
        print("🎉 ALL ENTITY EXTRACTION UNIT TESTS PASSED!")
        print("\n💡 Entity extraction is working correctly!")
    else:
        print("❌ Some entity extraction tests failed.")
        print("\n🔧 Issues to investigate:")
        if not test1:
            print("   • Basic entity extraction not working")
        if not test2:
            print("   • Pantheon entity extraction needs improvement")  
        if not test3:
            print("   • Global threats entity extraction needs improvement")
    
    print("\n📋 This focused test helps isolate entity extraction issues.") 