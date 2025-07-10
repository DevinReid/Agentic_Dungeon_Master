import cli
from services.game_session import GameSession
from services.character_creator import CharacterCreator
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
    
    # ? refactor
    def continue_most_recent_campaign(self, username):
        """Continue the most recent campaign for a user"""
        user_id = get_or_create_user(username)
        recent_campaign = get_most_recent_campaign(user_id)
        
        if not recent_campaign:
            print("No recent campaigns found! Create a new one first.")
            return None
        
        campaign_id, name, description, created_at, last_played, creator, role = recent_campaign
        print(f"Continuing: {name}")
        
        return self.select_character(campaign_id, username, is_new=False)
        
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

    def select_character(self, campaign_id, username, is_new=False):
        """Run a campaign session"""
        
        campaign_manager = CampaignManager()
        
        while True:
            # Show campaign info
            print(f"\nCampaign ID: {campaign_id}... | User: {username}")
            
            # Use appropriate scrollable menu based on campaign type
            if is_new:
                choice = cli.ui_character_menu_new_campaign()
            else:
                choice = cli.ui_character_menu_existing_campaign()
            
            is_new = False  # Reset flag after first iteration
            
            if choice == "Create New Character":
                # Create new character
                game_session = CharacterCreator(campaign_id, username).create_new_character()
                if game_session:
                    # Update campaign last played time
                    campaign_manager.update_last_played(campaign_id)
                    self.run_game_session(game_session, is_new_character=True)
                    
            elif choice == "🔴 Load Existing Character":
                # Load existing character (only available for existing campaigns)
                game_session = self.load_existing_character(campaign_id, username)
                if game_session:
                    # Update campaign last played time
                    campaign_manager.update_last_played(campaign_id)
                    self.run_game_session(game_session, is_new_character=False)
                    
                    
            elif choice == "Back to Main Menu":
                return None  # Return to main menu


    def load_existing_character(self,campaign_id, username):
        """Load existing character for a campaign"""
        
        # Create game session with campaign context - it will auto-load character
        game_session = GameSession(campaign_id, username)
        
        if not game_session.character:
            print("No character found in this campaign!")
            return None
            
        print(f"Loaded character: {game_session.player_name} ({game_session.player_class})")
        return game_session
    
    
    def run_game_session(self,game_session, is_new_character=False):
        """Run the actual game session"""
        
        print(f"\nStarting session for {game_session.player_name} ({game_session.player_class})")
        
        cli.ui_intro_text()
        cli.ui_player_character_sheet(game_session.character)
        
        # Run intro scene
        if is_new_character:    
            intro_text = game_session.run_intro_scene()
            print(f"\n{intro_text}")
        else:
            print(f"\nWelcome back, {game_session.player_name}! Your adventure continues...")
            print(f"\n{game_session.last_dm_text}") # add a summary here!
        
        # Main game loop
        while True:
            action = cli.ui_get_action()
            
            # Process the action (command handler will handle menu/other commands)
            result = game_session.action_handler(action)
            
            if result == "exit_to_menu":
                return  # Exit to campaign menu
            elif result == "command_handled":
                continue  # Command was handled, ask for next action
            elif result == "combat":
                # Start combat
                combat_result = game_session.start_combat()
                if combat_result == "exit_to_menu":
                    return  # Player chose to exit to menu from combat
                elif combat_result == "game_over":
                    return  # Character died, exit to menu
                else:
                    # Combat ended, continue story
                    print(f"\n{combat_result}")
            elif result == "game_over":
                return  # Game over, exit to menu
            else:
                # Normal story continuation
                print(f"\n{result}")