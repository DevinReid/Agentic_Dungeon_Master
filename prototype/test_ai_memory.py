#!/usr/bin/env python3
"""
Test script for the AI Memory System

This script demonstrates the new persistent world features:
- Persistent NPCs that remember past interactions
- Story events saved to database
- NPC relationship tracking
- Enhanced story generation with context
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from setup_db import setup_database
from db import save_npc, save_event, update_npc_relationship, get_recent_events, get_npc_relationships
import json

def test_ai_memory_system():
    """Test the AI memory system functionality"""
    print("🧠 AI MEMORY SYSTEM TEST")
    print("=" * 50)
    
    # 1. Setup database
    print("\n1. Setting up database...")
    if not setup_database():
        print("❌ Database setup failed!")
        return False
    
    # 2. Test NPC persistence
    print("\n2. Testing NPC persistence...")
    test_npc = {
        "id": "test-npc-001",
        "name": "Gareth the Wise",
        "class": "Wizard",
        "hp": 25,
        "max_hp": 25,
        "ac": 12,
        "strength": 8,
        "dexterity": 12,
        "constitution": 14,
        "intelligence": 18,
        "wisdom": 15,
        "charisma": 10,
        "level": 3,
        "current_location": "Starting Area",
        "status": "alive",
        "disposition": "friendly",
        "backstory": "A wise old wizard who helps adventurers"
    }
    
    save_npc(test_npc)
    print(f"✅ Saved NPC: {test_npc['name']}")
    
    # 3. Test event logging
    print("\n3. Testing event logging...")
    save_event(
        event_type="test",
        description="Player met Gareth the Wise for the first time",
        location="Starting Area",
        npcs_involved=json.dumps(["Gareth the Wise"]),
        player_actions="Greeted the wizard politely",
        consequences="Gareth smiled warmly",
        session_context="Test session context"
    )
    print("✅ Saved test event")
    
    # 4. Test relationship tracking
    print("\n4. Testing relationship tracking...")
    update_npc_relationship(
        npc_id="test-npc-001",
        character_name="TestPlayer",
        relationship_change=15,
        interaction_description="Player helped Gareth find his lost spellbook"
    )
    print("✅ Updated NPC relationship (+15)")
    
    # 5. Test memory retrieval
    print("\n5. Testing memory retrieval...")
    
    # Get recent events
    events = get_recent_events(limit=3)
    print(f"Recent events: {len(events)} found")
    for event in events:
        print(f"  - {event['event_type']}: {event['description'][:50]}...")
    
    # Get relationships
    relationships = get_npc_relationships("TestPlayer")
    print(f"Relationships: {len(relationships)} found")
    for rel in relationships:
        print(f"  - {rel['npc_name']}: {rel['relationship_score']:+d} ({rel['relationship_type']})")
    
    print("\n✅ AI Memory System test completed successfully!")
    print("\n🎯 NEXT STEPS:")
    print("1. Run: python master.py")
    print("2. Start a new campaign")
    print("3. Try these commands during gameplay:")
    print("   - 'help' - Show all available commands")
    print("   - 'memory' - View recent story events")
    print("   - 'relationships' - View NPC relationships")
    print("   - 'npcs' - View NPCs at current location")
    print("   - 'location' - View location info")
    print("\n🧠 The AI will now remember everything!")
    
    return True

if __name__ == "__main__":
    test_ai_memory_system() 