import cli
from services.campaign_manager import CampaignManager
from services.world_builder import WorldGenerationOrchestrator
from db.db import delete_campaign_from_database



def start_menu():
    """Handle campaign selection/creation using scrollable CLI menu"""
    
    # For simplicity, use a default username (could ask user in future)
    username = "Player1"  # Could be extended to multi-user
    
    while True:
        choice = cli.ui_main_menu()
        
        campaign_manager = CampaignManager()
        
        if choice == "Play":
            result = campaign_manager.continue_most_recent_campaign(username)
            if result:
                return result  # campaign_manager handles the run_campaign call
            continue
            
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
            orchestrator = WorldGenerationOrchestrator()
            world_created = orchestrator.world_creation__campaign_menu(campaign_id, campaign_name)
            if not world_created:
                print("Campaign creation cancelled.")
                continue
            
            return campaign_manager.select_character(campaign_id, username, is_new=True)
                
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
                    return campaign_manager.select_character(campaign_id, username, is_new=False)
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
        
    
def handle_campaign_deletion(username):
    """Handle campaign deletion with double confirmation"""
    from InquirerPy import inquirer
    
    campaign_manager = CampaignManager()
    campaigns = campaign_manager.list_user_campaigns(username)
    
    if not campaigns:
        print("\n❌ No campaigns found to delete!")
        input("Press Enter to continue...")
        return
    
    print("\n🗑️ DELETE CAMPAIGN")
    print("="*50)
    print("⚠️  WARNING: This will permanently delete the campaign and ALL associated data!")
    print("   (Characters, NPCs, Events, Relationships, Locations, etc.)")
    print()
    
    # Show campaigns with detailed info
    campaign_choices = []
    for i, campaign in enumerate(campaigns):
        campaign_id, name, description, created_at, last_played, creator, role = campaign
        created_str = created_at.strftime("%Y-%m-%d") if created_at else "Unknown"
        last_played_str = last_played.strftime("%Y-%m-%d") if last_played else "Never"
        
        display_text = f"{name} (Created: {created_str}, Last Played: {last_played_str})"
        if description:
            display_text += f" - {description}"
            
        campaign_choices.append(display_text)
    
    # Add cancel option
    campaign_choices.append("❌ Cancel - Don't delete anything")
    
    # First selection: Choose campaign
    selected_campaign = inquirer.select(
        message="Which campaign do you want to DELETE?",
        choices=campaign_choices
    ).execute()
    
    if "❌ Cancel" in selected_campaign:
        print("✅ Campaign deletion cancelled.")
        return
    
    # Find the selected campaign
    selected_index = campaign_choices.index(selected_campaign)
    campaign_to_delete = campaigns[selected_index]
    campaign_id, name, description, created_at, last_played, creator, role = campaign_to_delete
    
    # First confirmation
    print(f"\n⚠️  You selected: '{name}' for deletion")
    print("This action CANNOT be undone!")
    
    first_confirm = inquirer.select(
        message=f"Are you SURE you want to delete '{name}' and all its data?",
        choices=[
            "❌ No, cancel deletion",
            f"🗑️ Yes, delete '{name}'"
        ]
    ).execute()
    
    if "❌ No" in first_confirm:
        print("✅ Campaign deletion cancelled.")
        return
    
    # Second confirmation (double-check)
    print("\n🚨 FINAL WARNING 🚨")
    print(f"Campaign: '{name}'")
    print("This will DELETE:")
    print("  • The campaign itself")
    print("  • All characters in this campaign")
    print("  • All NPCs and their relationships")
    print("  • All story events and memories")
    print("  • All locations and world data")
    print("  • EVERYTHING associated with this campaign")
    print()
    
    second_confirm = inquirer.select(
        message="Type the campaign name to confirm deletion:",
        choices=[
            "❌ Cancel - I changed my mind",
            f"🗑️ DELETE '{name}' - I understand this cannot be undone"
        ]
    ).execute()
    
    if "❌ Cancel" in second_confirm:
        print("✅ Campaign deletion cancelled.")
        return
    
    # Perform the deletion
    try:
        print(f"\n🗑️ Deleting campaign '{name}'...")
        success = delete_campaign_from_database(campaign_id)
        
        if success:
            print(f"✅ Campaign '{name}' and all associated data has been permanently deleted.")
        else:
            print(f"❌ Failed to delete campaign '{name}'. Please try again.")
            
    except Exception as e:
        print(f"❌ Error deleting campaign: {str(e)}")
    
    input("\nPress Enter to continue...")


def handle_options_menu(username):
    """Handle the options and settings menu"""
    while True:
        choice = cli.ui_options_menu()
        
        if choice == "🌍 World Builder":
            world_builder_cli = cli.WorldBuilderCLI()
            world_builder_cli.show_world_builder_menu()
            
        elif choice == "🗑️ Delete Campaign":
            handle_campaign_deletion(username)
            
        elif choice == "⚙️ Game Settings (coming soon)":
            print("\n⚙️ Game Settings")
            print("Coming soon! This will include:")
            print("  • Difficulty settings")
            print("  • AI behavior preferences")
            print("  • Display options")
            input("\nPress Enter to continue...")
            
        elif choice == "🔧 Debug Tools (coming soon)":
            print("\n🔧 Debug Tools")
            print("Coming soon! This will include:")
            print("  • Database viewer")
            print("  • AI prompt debugging")
            print("  • System diagnostics")
            input("\nPress Enter to continue...")
            
        elif choice == "🔙 Back to Main Menu":
            return  # Exit options menu, return to main menu
        
        # Continue the options menu loop for other choices
