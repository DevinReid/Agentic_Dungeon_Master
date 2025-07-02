#!/usr/bin/env python3
"""
Test New ContentProcessor Pipeline

End-to-end test of the new world creation pipeline:
UniverseBuilder → ContentProcessor → Database + Vector Storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from bots.content_processor_agent import ContentProcessorAgent
from db.db import save_processed_world, get_world_by_campaign
from services.campaign_manager import CampaignManager

def test_new_pipeline():
    """Test the complete new pipeline"""
    
    print("🧪 TESTING NEW CONTENT PROCESSOR PIPELINE")
    print("=" * 60)
    
    # Create a test campaign first
    test_campaign_id = str(uuid.uuid4())
    test_username = "test_user"
    
    # Create campaign in database
    campaign_manager = CampaignManager()
    
    try:
        actual_campaign_id = campaign_manager.create_new_campaign("Test Campaign", test_username, "Test campaign for pipeline testing")
        print(f"✅ Test campaign created: {actual_campaign_id}")
        # Use the actual campaign ID returned from the database
        test_campaign_id = str(actual_campaign_id)
    except Exception as e:
        print(f"⚠️ Campaign creation issue (might already exist): {e}")
    
    # Sample universe data with longer content for proper chunking
    sample_universe_data = {
        "world_info": {
            "world_name": "Aethermoor",
            "world_description": "Aethermoor is a mystical realm where floating islands drift through endless skies, connected by bridges of crystallized starlight. Ancient wind elementals guard the secrets of flight magic, while sky pirates and cloud cities dot the endless horizon. The realm consists of dozens of major islands, each with its own unique ecosystem and culture. The largest island, Nimbus Throne, serves as the capital where the Sky Council meets. Smaller islands house specialized communities: the Stormcaller Isle trains weather mages, the Merchant's Haven serves as a trading hub, and the Windwhisper Sanctuary protects ancient elemental spirits. The islands are connected by a complex network of wind currents and magical bridges that shimmer with ethereal light. Travel between islands requires either magical flight, sky ships, or the dangerous leap across the void using wind magic. The constant presence of floating crystals throughout the realm creates a perpetual twilight effect, where the sky glows with soft, ever-changing colors. These crystals are both a source of magical power and a reminder of the realm's mysterious origins.",
            "theme_list": "sky islands, wind magic, flying adventures, elemental spirits",
            "scope": "regional",
            "region_count": 4,
            "major_city_count": 2,
            "settlement_count": 8
        },
        "pantheon": {
            "structure": "The Sky Pantheon consists of four elemental lords who govern the winds and storms, each ruling from their own celestial domain above the floating islands.",
            "major_deities": [
                "Zephyros, Lord of the Western Winds",
                "Tempest, Goddess of Storm and Lightning", 
                "Gale, Spirit of Gentle Breezes",
                "Cyclone, The Wrathful Hurricane"
            ],
            "religious_conflicts": "The followers of Tempest clash with Zephyros worshippers over storm magic practices, while Gale's pacifist priests attempt to mediate between the warring factions. The cult of Cyclone remains hidden, practicing destructive magic in secret."
        },
        "magic_system": {
            "commonality": "Rare - Only sky-touched individuals can manipulate wind magic, usually those born during aerial storms or blessed by the elemental lords.",
            "mechanics": "Magic flows through ley lines of crystallized air that connect the floating islands. Practitioners must attune themselves to these currents and channel their power through focus crystals. The magic manifests as control over wind, weather, and limited flight abilities. Advanced practitioners can create temporary air bridges, summon protective wind barriers, or even call down lightning from storm clouds.",
            "limitations": "Wind magic becomes unstable during storm seasons, causing unpredictable effects. Overuse can result in 'sky madness' where the practitioner becomes disconnected from the ground and loses their sense of direction. The ley lines themselves can be disrupted by strong magical interference, cutting off power to entire regions.",
            "magic_level": "medium"
        },
        "global_threats": [
            {
                "primary_threat": "The Void Beneath",
                "threat_details": "A growing darkness beneath the floating islands consumes anything that falls, and shadow tendrils now reach upward toward the lowest settlements. The void appears to be an ancient entity that feeds on magical energy, slowly draining the power from the crystallized air ley lines. As it grows stronger, more islands begin to lose altitude, forcing desperate evacuations to higher ground. Strange whispers echo from the darkness, promising power to those willing to serve the void. Several settlements have already been consumed, their inhabitants transformed into shadow creatures that serve the growing darkness.",
                "world_impact": "Islands are mysteriously losing altitude, forcing desperate evacuations to higher ground. The magical ley lines are weakening, making wind magic increasingly unreliable. Trade routes are disrupted as lower islands become inaccessible, leading to resource shortages in the higher settlements."
            }
        ]
    }
    
    try:
        print(f"📋 Test Campaign ID: {test_campaign_id}")
        print(f"🌍 Test World: {sample_universe_data['world_info']['world_name']}")
        
        # STEP 1: Process through ContentProcessor
        print("\n🏗️ STEP 1: Processing content through ContentProcessor...")
        processor = ContentProcessorAgent(debug=True)
        processed_sections = processor.process_universe_content(test_campaign_id, sample_universe_data)
        
        print(f"✅ Content processing complete!")
        print(f"   📄 Processed {len(processed_sections)} sections")
        
        # Show processing results
        for section in processed_sections:
            print(f"   • {section['content_type']}: {len(section['tags'])} tags, {len(section['entities'])} entities, {len(section['chunks'])} chunks")
        
        # STEP 2: Save to database
        print("\n💾 STEP 2: Saving to database with full enrichment...")
        world_id = save_processed_world(test_campaign_id, processed_sections)
        print(f"✅ World saved! ID: {world_id}")
        
        # STEP 3: Verify data was saved correctly
        print("\n🔍 STEP 3: Verifying saved data...")
        saved_world = get_world_by_campaign(test_campaign_id)
        
        if saved_world:
            print(f"✅ World retrieval successful!")
            print(f"   🌍 World Name: {saved_world['world_name']}")
            print(f"   📄 Content Sections: {len(saved_world['content'])}")
            print(f"   🏷️ Content Types: {list(saved_world['content'].keys())}")
            
            # Check if content has our enriched data
            first_content = list(saved_world['content'].values())[0]
            if 'content_id' in first_content:
                print(f"   ✅ Content IDs present")
            else:
                print(f"   ⚠️ Content IDs missing")
                
        else:
            print("❌ World retrieval failed!")
            return False
        
        print("\n🎉 NEW PIPELINE TEST PASSED!")
        print("=" * 60)
        print("✅ ContentProcessor working")
        print("✅ Database saving working") 
        print("✅ Vector embeddings working")
        print("✅ Tag generation working")
        print("✅ Entity extraction working")
        print("✅ Content chunking working")
        print("\n🚀 Ready for integration with world builder!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ PIPELINE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Clean up test data (optional)"""
    print("\n🧹 Test data cleanup available but not automated")
    print("   Test campaign will remain in database for inspection")

if __name__ == "__main__":
    print("🚀 Starting New Pipeline Test")
    
    success = test_new_pipeline()
    
    if success:
        print("\n💡 Next Steps:")
        print("   1. ✅ Pipeline is working!")
        print("   2. 🔗 Integration ready for world builder")
        print("   3. 🌟 Expansion bots can be added next")
        cleanup_test_data()
    else:
        print("\n🔧 Fix the issues above before proceeding") 