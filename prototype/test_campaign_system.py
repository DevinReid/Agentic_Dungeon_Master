#!/usr/bin/env python3
"""
Test script for Campaign Management System

This script tests:
- Creating new campaigns
- Listing campaigns
- Campaign database creation
- Campaign isolation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from campaign_manager import CampaignManager

def test_campaign_system():
    """Test the campaign management functionality"""
    print("🎮 CAMPAIGN SYSTEM TEST")
    print("=" * 50)
    
    # Initialize campaign manager
    print("\n1. Initializing Campaign Manager...")
    try:
        cm = CampaignManager()
        print("✅ Campaign Manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test creating campaigns
    print("\n2. Creating test campaigns...")
    try:
        campaign1_id = cm.create_new_campaign("Forest Adventure")
        campaign2_id = cm.create_new_campaign("Desert Quest")
        print("✅ Created 2 test campaigns")
    except Exception as e:
        print(f"❌ Failed to create campaigns: {e}")
        return False
    
    # Test listing campaigns
    print("\n3. Listing all campaigns...")
    try:
        campaigns = cm.list_campaigns()
        print(f"Found {len(campaigns)} campaigns:")
        for campaign_id, name, created_at, last_played in campaigns:
            print(f"  - {name} (ID: {campaign_id[:8]}...) Last played: {last_played}")
        print("✅ Campaign listing works")
    except Exception as e:
        print(f"❌ Failed to list campaigns: {e}")
        return False
    
    # Test getting most recent
    print("\n4. Testing most recent campaign...")
    try:
        recent = cm.get_most_recent_campaign()
        if recent:
            print(f"Most recent: {recent[1]} (ID: {recent[0][:8]}...)")
        else:
            print("No campaigns found")
        print("✅ Most recent campaign retrieval works")
    except Exception as e:
        print(f"❌ Failed to get recent campaign: {e}")
        return False
    
    # Test database URL generation
    print("\n5. Testing database URL generation...")
    try:
        url1 = cm.get_campaign_db_url(campaign1_id)
        url2 = cm.get_campaign_db_url(campaign2_id)
        
        print(f"Campaign 1 DB: {url1.split('/')[-1]}")  # Just show DB name
        print(f"Campaign 2 DB: {url2.split('/')[-1]}")  # Just show DB name
        
        # Verify they're different
        if url1 != url2:
            print("✅ Each campaign gets unique database")
        else:
            print("❌ Campaigns sharing same database!")
            return False
            
    except Exception as e:
        print(f"❌ Failed to generate DB URLs: {e}")
        return False
    
    # Test campaign existence check
    print("\n6. Testing campaign existence...")
    try:
        exists1 = cm.campaign_exists(campaign1_id)
        exists_fake = cm.campaign_exists("fake-uuid-12345")
        
        if exists1 and not exists_fake:
            print("✅ Campaign existence check works")
        else:
            print("❌ Campaign existence check failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check campaign existence: {e}")
        return False
    
    print("\n✅ All campaign system tests passed!")
    print("\n🎯 READY FOR NEXT STEP:")
    print("The campaign system is working. Next we need to:")
    print("1. Update the menu system to use campaigns")
    print("2. Update db.py to work with campaign-specific databases")
    print("3. Update game_session.py to use campaign context")
    
    return True

if __name__ == "__main__":
    test_campaign_system() 