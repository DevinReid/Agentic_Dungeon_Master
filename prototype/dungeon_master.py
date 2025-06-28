# dungeon_master.py
import cli
from services.game_session import GameSession
from services.campaign_manager import CampaignManager
from db.db import get_or_create_user
import uuid

def create_new_character(campaign_id, username):
    """Create a new character for a campaign"""
    
    # Get character details from CLI
    name = cli.ui_get_char_name()
    char_class = cli.ui_get_char_class()
    
    # Start game session with campaign context
    game_session = GameSession(campaign_id, username)
    game_session.setup_character(name, char_class)
    
    return game_session

def load_existing_character(campaign_id, username):
    """Load existing character for a campaign"""
    
    # Create game session with campaign context - it will auto-load character
    game_session = GameSession(campaign_id, username)
    
    if not game_session.character:
        print("❌ No character found in this campaign!")
        return None
        
    print(f"✅ Loaded character: {game_session.player_name} ({game_session.player_class})")
    return game_session

def campaign_menu():
    """Handle campaign selection/creation"""
    print("\n" + "="*50)
    print("🎮 D&D CAMPAIGN MANAGER")
    print("="*50)
    
    # For simplicity, use a default username (could ask user in future)
    username = "Player1"  # Could be extended to multi-user
    
    campaign_manager = CampaignManager()
    
    while True:
        print(f"\n👤 Playing as: {username}")
        print("\n📁 CAMPAIGN OPTIONS:")
        print("1. 🆕 Create New Campaign")
        print("2. 📋 Select Existing Campaign") 
        print("3. 🔄 Continue Most Recent Campaign")
        print("4. ❌ Quit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            # Create new campaign
            campaign_name = input("\n📝 Enter campaign name: ").strip()
            if not campaign_name:
                print("❌ Campaign name cannot be empty!")
                continue
                
            description = input("📝 Enter campaign description (optional): ").strip()
            
            campaign_id = campaign_manager.create_new_campaign(campaign_name, username, description)
            print(f"✅ Created campaign: {campaign_name}")
            
            return run_campaign(campaign_id, username, is_new=True)
            
        elif choice == "2":
            # Select existing campaign
            campaigns = campaign_manager.list_user_campaigns(username)
            
            if not campaigns:
                print("❌ No campaigns found! Create a new one first.")
                continue
                
            print("\n📋 YOUR CAMPAIGNS:")
            for i, campaign in enumerate(campaigns, 1):
                campaign_id, name, description, created_at, last_played, creator, role = campaign
                last_played_str = last_played.strftime("%Y-%m-%d %H:%M") if last_played else "Never"
                print(f"{i}. {name} ({role}) - Last played: {last_played_str}")
                if description:
                    print(f"   Description: {description}")
                    
            try:
                selection = int(input(f"\nSelect campaign (1-{len(campaigns)}): ")) - 1
                if 0 <= selection < len(campaigns):
                    selected_campaign = campaigns[selection]
                    campaign_id = selected_campaign[0]
                    return run_campaign(campaign_id, username, is_new=False)
                else:
                    print("❌ Invalid selection!")
            except ValueError:
                print("❌ Please enter a valid number!")
                
        elif choice == "3":
            # Continue most recent campaign
            recent_campaign = campaign_manager.get_most_recent_campaign_for_user(username)
            
            if not recent_campaign:
                print("❌ No recent campaigns found! Create a new one first.")
                continue
                
            campaign_id, name, description, created_at, last_played, creator, role = recent_campaign
            print(f"🔄 Continuing: {name}")
            
            return run_campaign(campaign_id, username, is_new=False)
            
        elif choice == "4":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice! Please enter 1-4.")

def run_campaign(campaign_id, username, is_new=False):
    """Run a campaign session"""
    
    campaign_manager = CampaignManager()
    
    while True:
        print("\n" + "="*50)
        print(f"🎮 CAMPAIGN SESSION")
        print(f"📁 Campaign ID: {str(campaign_id)[:8]}...")
        print(f"👤 User: {username}")
        print("="*50)
        
        print("\n🎯 GAME OPTIONS:")
        if is_new:
            print("1. 🆕 Create New Character")
            print("2. 🔙 Back to Campaign Menu")
            is_new = False  # Reset flag after first iteration
        else:
            print("1. 🆕 Create New Character")
            print("2. 📖 Load Existing Character") 
            print("3. 🔙 Back to Campaign Menu")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            game_session = create_new_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session)
                
        elif choice == "2" and not is_new:
            game_session = load_existing_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session)
                
        elif choice == "3" or (choice == "2" and is_new):
            return campaign_menu()  # Back to campaign selection
        else:
            print("❌ Invalid choice!")

def run_game_session(game_session):
    """Run the actual game session"""
    
    print(f"\n🎮 Starting session for {game_session.player_name} ({game_session.player_class})")
    
    cli.ui_intro_text()
    cli.ui_player_character_sheet(game_session.character)
    
    # Run intro scene
    intro_text = game_session.run_intro_scene()
    print(f"\n{intro_text}")
    
    # Main game loop
    while True:
        action = cli.ui_get_action()
        
        # Handle special commands
        if action.lower() == "menu":
            return  # Exit to campaign menu
        
        # Process the action
        result = game_session.action_handler(action)
        
        if result == "combat":
            # Start combat
            combat_result = game_session.start_combat()
            if combat_result == "game_over":
                return  # Character died, exit to menu
            else:
                # Combat ended, continue story
                print(f"\n{combat_result}")
        elif result == "game_over":
            return  # Game over, exit to menu
        else:
            # Normal story continuation
            print(f"\n{result}")

def main():
    """Main entry point"""
    print("🏰 Welcome to the Agentic D&D Dungeon Master!")
    print("🧠 Featuring AI Memory - NPCs remember your actions!")
    
    try:
        campaign_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your database connection and try again.")

if __name__ == "__main__":
    main()
