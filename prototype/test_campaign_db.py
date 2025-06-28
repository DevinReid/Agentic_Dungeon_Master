#!/usr/bin/env python3
"""
Test campaign-aware database functions
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from campaign_manager import CampaignManager
from db import (create_character, get_character_sheet, save_npc, get_npcs_at_location, 
                save_event, get_recent_events, update_npc_relationship, get_npc_relationships)
import json

def test_campaign_db():
    print("🗄️ CAMPAIGN DATABASE TEST")
    print("=" * 50)
    
    # Create two test campaigns
    cm = CampaignManager()
    campaign1_id = cm.create_new_campaign("Test Campaign 1")
    campaign2_id = cm.create_new_campaign("Test Campaign 2")
    
    # Test character isolation
    print("\n1. Testing character isolation...")
    create_character(campaign1_id, "Alice", "Fighter", 100)
    create_character(campaign2_id, "Bob", "Wizard", 50)
    
    char1 = get_character_sheet(campaign1_id)
    char2 = get_character_sheet(campaign2_id)
    
    if char1[0] == "Alice" and char2[0] == "Bob":
        print("✅ Characters properly isolated")
    else:
        print("❌ Character isolation failed")
        return False
    
    # Test NPC isolation
    print("\n2. Testing NPC isolation...")
    npc1 = {
        "id": "npc-1", "name": "Guard", "class": "Fighter", "hp": 30, "ac": 16,
        "strength": 15, "dexterity": 12, "constitution": 14, "intelligence": 10,
        "wisdom": 11, "charisma": 10, "level": 2, "current_location": "Gate"
    }
    npc2 = {
        "id": "npc-2", "name": "Merchant", "class": "Noble", "hp": 20, "ac": 12,
        "strength": 10, "dexterity": 14, "constitution": 12, "intelligence": 16,
        "wisdom": 13, "charisma": 15, "level": 1, "current_location": "Market"
    }
    
    save_npc(campaign1_id, npc1)
    save_npc(campaign2_id, npc2)
    
    npcs1 = get_npcs_at_location(campaign1_id, "Gate")
    npcs2 = get_npcs_at_location(campaign2_id, "Market")
    
    if len(npcs1) == 1 and npcs1[0]["name"] == "Guard" and len(npcs2) == 1 and npcs2[0]["name"] == "Merchant":
        print("✅ NPCs properly isolated")
    else:
        print("❌ NPC isolation failed")
        return False
    
    # Test event isolation
    print("\n3. Testing event isolation...")
    save_event(campaign1_id, "test", "Alice met the Guard", "Gate", json.dumps(["Guard"]), "Hello", "Guard waved")
    save_event(campaign2_id, "test", "Bob bought supplies", "Market", json.dumps(["Merchant"]), "Buy bread", "Merchant sold bread")
    
    events1 = get_recent_events(campaign1_id, 5)
    events2 = get_recent_events(campaign2_id, 5)
    
    if len(events1) == 1 and "Alice" in events1[0]["description"] and len(events2) == 1 and "Bob" in events2[0]["description"]:
        print("✅ Events properly isolated")
    else:
        print("❌ Event isolation failed")
        return False
    
    # Test relationship isolation
    print("\n4. Testing relationship isolation...")
    update_npc_relationship(campaign1_id, "npc-1", "Alice", 10, "Alice was polite to Guard")
    update_npc_relationship(campaign2_id, "npc-2", "Bob", -5, "Bob haggled aggressively")
    
    rels1 = get_npc_relationships(campaign1_id, "Alice")
    rels2 = get_npc_relationships(campaign2_id, "Bob")
    
    if (len(rels1) == 1 and rels1[0]["relationship_score"] == 10 and 
        len(rels2) == 1 and rels2[0]["relationship_score"] == -5):
        print("✅ Relationships properly isolated")
    else:
        print("❌ Relationship isolation failed")
        return False
    
    print("\n✅ All campaign database tests passed!")
    print("🎯 Data is properly isolated between campaigns")
    return True

if __name__ == "__main__":
    test_campaign_db() 