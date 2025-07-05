import cli
from db.db import CampaignManager


def start_menu():
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
            
            # NEW: World creation choice
            world_created = handle_world_creation_for_campaign(campaign_id, campaign_name)
            if not world_created:
                print("Campaign creation cancelled.")
                continue
            
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
            # Handle options menu
            handle_options_menu(username)
            continue
            
        elif choice == "Quit":
            print("Goodbye!")
            return