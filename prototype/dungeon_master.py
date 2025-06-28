# dungeon_master.py
import cli
from services.game_session import GameSession
from services.campaign_manager import CampaignManager


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
        print("No character found in this campaign!")
        return None
        
    print(f"Loaded character: {game_session.player_name} ({game_session.player_class})")
    return game_session

def campaign_menu():
    """Handle campaign selection/creation using scrollable CLI menu"""
    
    # For simplicity, use a default username (could ask user in future)
    username = "Player1"  # Could be extended to multi-user
    
    while True:
        choice = cli.ui_main_menu()
        
        campaign_manager = CampaignManager()
        
        if choice == "Play":
            # Continue most recent campaign
            recent_campaign = campaign_manager.get_most_recent_campaign_for_user(username)
            
            if not recent_campaign:
                print("No recent campaigns found! Create a new one first.")
                continue
            
            campaign_id, name, description, created_at, last_played, creator, role = recent_campaign
            print(f"Continuing: {name}")
            
            return run_campaign(campaign_id, username, is_new=False)
            
        elif choice == "Start New Campaign":
            # Create new campaign
            campaign_name = input("\nEnter campaign name: ").strip()
            if not campaign_name:
                print("Campaign name cannot be empty!")
                continue
                
            description = input("Enter campaign description (optional): ").strip()
            
            campaign_id = campaign_manager.create_new_campaign(campaign_name, username, description)
            print(f"Created campaign: {campaign_name}")
            
            return run_campaign(campaign_id, username, is_new=True)
                
        elif choice == "Load Previous Campaign":
            # Select existing campaign
            campaigns = campaign_manager.list_user_campaigns(username)
            
            if not campaigns:
                print("No campaigns found! Create a new one first.")
                continue
                
            print("\nYOUR CAMPAIGNS:")
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
                    print("Invalid selection!")
            except ValueError:
                print("Please enter a valid number!")
                
        elif choice == "Options":
            # Placeholder for options menu
            print("Options menu - coming soon!")
            continue
            
        elif choice == "Quit":
            print("Goodbye!")
            return

def run_campaign(campaign_id, username, is_new=False):
    """Run a campaign session"""
    
    campaign_manager = CampaignManager()
    
    while True:
        # Show campaign info
        print(f"\nCampaign ID: {str(campaign_id)[:8]}... | User: {username}")
        
        # Use appropriate scrollable menu based on campaign type
        if is_new:
            choice = cli.ui_character_menu_new_campaign()
        else:
            choice = cli.ui_character_menu_existing_campaign()
        
        is_new = False  # Reset flag after first iteration
        
        if choice == "🔴 Create New Character":
            # Create new character
            game_session = create_new_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session)
                
        elif choice == "🔴 Load Existing Character":
            # Load existing character (only available for existing campaigns)
            game_session = load_existing_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session)
                
        elif choice == "Create New Character":
            # Create new character for existing campaign
            game_session = create_new_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session)
                
        elif choice == "Back to Main Menu":
            return campaign_menu()  # Back to main menu

def run_game_session(game_session):
    """Run the actual game session"""
    
    print(f"\nStarting session for {game_session.player_name} ({game_session.player_class})")
    
    cli.ui_intro_text()
    cli.ui_player_character_sheet(game_session.character)
    
    # Run intro scene
    intro_text = game_session.run_intro_scene()
    print(f"\n{intro_text}")
    
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

def main():
    """Main entry point"""
    print("Welcome to the Agentic D&D Dungeon Master!")

    
    try:
        campaign_menu()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your database connection and try again.")

if __name__ == "__main__":
    main()
