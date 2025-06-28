
from db.db import (create_campaign, list_campaigns, get_most_recent_campaign, 
                   update_campaign_last_played, get_or_create_user)

class CampaignManager:
    def __init__(self):
        print("✅ Campaign Manager initialized with new schema")
    
    def create_new_campaign(self, campaign_name, username, description=""):
        """Create a new campaign for a user"""
        # Get or create user
        user_id = get_or_create_user(username)
        
        # Create campaign
        campaign_id = create_campaign(campaign_name, description, user_id)
        
        print(f"🎮 Created campaign: '{campaign_name}' (ID: {str(campaign_id)[:8]}...)")
        return campaign_id
    
    def list_user_campaigns(self, username):
        """List all campaigns for a user"""
        user_id = get_or_create_user(username)
        return list_campaigns(user_id)
    
    def get_most_recent_campaign_for_user(self, username):
        """Get the most recently played campaign for a user"""
        user_id = get_or_create_user(username)
        return get_most_recent_campaign(user_id)
    
    def update_last_played(self, campaign_id):
        """Update when campaign was last played"""
        update_campaign_last_played(campaign_id)
    
    def campaign_exists(self, campaign_id):
        """Check if campaign exists (simple check by trying to get campaigns)"""
        try:
            campaigns = list_campaigns()
            return any(str(c[0]) == str(campaign_id) for c in campaigns)
        except:
            return False
