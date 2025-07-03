#!/usr/bin/env python3
"""
Entity Extractor vs Processor Comparison Test

This test clearly shows the difference between:
1. Raw entities from EntityExtractorAgent 
2. Complete processed entities from EntityProcessorAgent

Shows exactly what each stage produces.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import json
from bots.entity_extractor_agent import EntityExtractorAgent
from bots.entity_processor_agent import EntityProcessorAgent

def test_extractor_vs_processor():
    """Test to show exact output differences between extractor and processor"""
    
    # Sample content for testing
    test_content = """
    Deep beneath the Crystalline Mountains, the Dread Titan known as Malakar stirs from its 
    millennia-long slumber. The ancient evil has been bound by three sacred artifacts: the 
    Crown of Binding held by High Priestess Serana in the Temple of Light, the Staff of 
    Warding guarded by the Order of the Dawn in their fortress of Shadowhold, and the 
    Heart of Nature protected by the druids in the Sacred Grove.
    
    The awakening of Malakar threatens to shatter the delicate balance of the world. His 
    cultists, led by the fallen paladin Sir Darius Blackheart, seek to claim these artifacts 
    and release their dark master. The only hope lies in the prophecy that speaks of a 
    chosen champion who will unite the three sacred relics.
    """
    
    test_campaign_id = str(uuid.uuid4())
    existing_tags = ["global_threats", "ancient_evil", "sacred_artifacts", "prophecy"]
    
    # STEP 1: Raw Entity Extraction
    try:
        extractor = EntityExtractorAgent(debug=False)  # Turn off debug for cleaner output
        
        # Get raw entities (before processing)
        raw_entities = extractor._ai_extract_entities(
            content=test_content,
            content_type="global_threats", 
            existing_tags=existing_tags,
            existing_entities={'npc': [], 'location': [], 'organization': [], 'artifact': [], 'deity': [], 'threat': []}
        )
        
        print("RAW ENTITIES JSON:")
        print(json.dumps(raw_entities, indent=2))
        print(f"RAW ENTITIES CHARACTER COUNT: {len(json.dumps(raw_entities))}")
        
    except Exception as e:
        print(f"Raw extraction failed: {e}")
        return False
    
    # STEP 2: Processed Entity Generation
    try:
        processor = EntityProcessorAgent(debug=False)  # Turn off debug for cleaner output
        
        # Process the raw entities into complete database records
        processed_entities = processor.process_entities(
            raw_entities=raw_entities,
            campaign_id=test_campaign_id,
            content=test_content,
            content_type="global_threats"
        )
        
        print("PROCESSED ENTITIES JSON:")
        print(json.dumps(processed_entities, indent=2))
        print(f"PROCESSED ENTITIES CHARACTER COUNT: {len(json.dumps(processed_entities))}")
        
    except Exception as e:
        print(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_extractor_vs_processor()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!") 