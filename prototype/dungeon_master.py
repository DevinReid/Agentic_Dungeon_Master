# dungeon_master.py
import cli
from services.game_session import GameSession
from services.campaign_manager import CampaignManager
from db import db


def handle_region_building_for_campaign(campaign_id, campaign_name, world_id, universe_data):
    """Delegate region building to the world builder orchestrator"""
    from world_builder import WorldGenerationOrchestrator
    
    orchestrator = WorldGenerationOrchestrator()
    return orchestrator.handle_region_planning_for_campaign(campaign_id, campaign_name, world_id, universe_data)


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

def handle_world_creation_for_campaign(campaign_id, campaign_name):
    """Handle world creation choice for a new campaign"""
    from InquirerPy import inquirer
    
    print(f"\n🌍 WORLD SETUP FOR CAMPAIGN: {campaign_name}")
    print("="*60)
    
    world_choice = inquirer.select(
        message="What kind of world would you like for this campaign?",
        choices=[
            "🆕 Create a brand new world for this campaign",
            "🏛️ Use an existing world (coming soon)",
            "🎲 We will craft a world for you (auto-generate)",
            "❌ Cancel campaign creation"
        ]
    ).execute()
    
    if "❌ Cancel" in world_choice:
        return False
    elif "🎲 We will craft" in world_choice:
        return create_auto_world_for_campaign(campaign_id, campaign_name)
    elif "🏛️ Use an existing" in world_choice:
        print("🚧 Existing world selection coming soon!")
        print("📝 For now, you can add a world later from the World Builder menu.")
        return True
    elif "🆕 Create a brand new" in world_choice:
        return create_new_world_for_campaign(campaign_id, campaign_name)
    
    return True

def create_new_world_for_campaign(campaign_id, campaign_name):
    """Delegate world creation to the world builder orchestrator"""
    print(f"\n🏗️ CREATING WORLD FOR: {campaign_name}")
    print("="*60)
    
    try:
        # Delegate to CLI for world parameters and creation
        from cli import WorldBuilderCLI
        world_builder_cli = WorldBuilderCLI()
        
        # This will handle the entire world creation flow
        print("Let's build your world! This will be the foundation for your adventures.")
        world_params = world_builder_cli.get_world_parameters()
        
        # Delegate to world builder orchestrator
        from world_builder import WorldGenerationOrchestrator
        orchestrator = WorldGenerationOrchestrator()
        
        print("\n🔄 Generating your world... (this may take a moment)")
        result = orchestrator.generate_complete_world(campaign_id, world_params)
        
        if result.success:
            print(f"\n✅ World '{result.world_name}' created successfully!")
            print(f"📁 Linked to campaign: {campaign_name}")
            
            # PHASE 1: Save base content using new ContentProcessor pipeline
            try:
                print("🏗️ Processing and saving world content...")
                world_id = save_world_with_content_processing(campaign_id, result.world_data)
                print("✅ World saved successfully!")
                
                # PHASE 2: Optional expansion
                if offer_content_expansion():
                    print("🔄 Expanding world content... (this may take a few minutes)")
                    expand_world_content(campaign_id, world_id)
                else:
                    print("⏩ Skipping expansion - world ready to play!")
                
                # Handle region planning
                input("\n📖 Press Enter to continue to region planning...")
                region_success = handle_region_building_for_campaign(campaign_id, campaign_name, world_id, result.world_data)
                if not region_success:
                    return False
                    
            except Exception as save_error:
                print(f"⚠️ Warning: World created but database save failed: {str(save_error)}")
                print("💾 Your world is still usable for this session!")
            
            input("\n📖 Press Enter to continue to character creation...")
            return True
        else:
            print(f"\n❌ World creation failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"\n❌ World creation failed: {str(e)}")
        print("📝 You can add a world to this campaign later from the World Builder menu.")
        return True

def create_auto_world_for_campaign(campaign_id, campaign_name):
    """Create an auto-generated world using predefined parameters"""
    print(f"\n🎲 AUTO-CRAFTING WORLD FOR: {campaign_name}")
    print("="*60)
    print("We'll create a classic fantasy world perfect for adventures!")
    
    try:
        # Use predefined parameters for auto-generation
        auto_world_params = {
            'theme': 'High Fantasy - Magic is everywhere, heroes are legendary',
            'magic_commonality': 'Common - Most towns have a wizard or healer',
            'deity_structure': 'Pantheon - Multiple gods with distinct domains',
            'major_threat': 'Ancient Evil - Something terrible stirs from long slumber',
            'size': 'Regional - Small continent (3 kingdoms, 3-5 major cities, 15-20 settlements)',
            'custom_details': f'Classic fantasy adventure setting for the {campaign_name} campaign'
        }
        
        # Delegate to world builder orchestrator
        from world_builder import WorldGenerationOrchestrator
        orchestrator = WorldGenerationOrchestrator()
        
        print("🔄 Generating your world... (this may take a moment)")
        result = orchestrator.generate_complete_world(campaign_id, auto_world_params)
        
        if result.success:
            print(f"\n✅ World '{result.world_name}' auto-crafted successfully!")
            print(f"📁 Linked to campaign: {campaign_name}")
            print("🎯 Perfect for classic D&D adventures!")
            
            # PHASE 1: Save base content using new ContentProcessor pipeline
            try:
                print("🏗️ Processing and saving world content...")
                world_id = save_world_with_content_processing(campaign_id, result.world_data)
                print("✅ World saved successfully!")
                
                # PHASE 2: Auto-expand for enhanced experience
                print("🔄 Auto-expanding content for richer experience...")
                expand_world_content(campaign_id, world_id, auto_expand=True)
                
                # Handle region planning
                input("\n📖 Press Enter to continue to region planning...")
                region_success = handle_region_building_for_campaign(campaign_id, campaign_name, world_id, result.world_data)
                if not region_success:
                    return False
                    
            except Exception as save_error:
                print(f"⚠️ Warning: World created but database save failed: {str(save_error)}")
                print("💾 Your world is still usable for this session!")
            
            input("\n📖 Press Enter to continue to character creation...")
            return True
        else:
            print(f"\n❌ Auto-world creation failed: {result.error}")
            print("Don't worry, you can still play without a generated world!")
            input("📖 Press Enter to continue...")
            return True  # Continue anyway
            
    except Exception as e:
        print(f"\n❌ Auto-world creation failed: {str(e)}")
        print("Don't worry, you can still play without a generated world!")
        input("📖 Press Enter to continue...")
        return True  # Continue anyway

def save_world_with_content_processing(campaign_id: str, universe_data: dict) -> str:
    """
    Save world using new ContentProcessor pipeline
    
    Args:
        campaign_id: Campaign UUID
        universe_data: Raw UniverseBuilder output
        
    Returns:
        world_id: UUID of created world
    """
    from bots.content_processor_agent import ContentProcessorAgent
    
    # Process universe data through ContentProcessor
    processor = ContentProcessorAgent(debug=True)
    processed_sections = processor.process_universe_content(campaign_id, universe_data)
    
    # Save processed content to database with full enrichment
    world_name = universe_data.get('world_info', {}).get('world_name')
    world_id = db.save_processed_world(campaign_id, processed_sections, world_name)
    
    return world_id

def offer_content_expansion() -> bool:
    """Ask user if they want to expand content"""
    from InquirerPy import inquirer
    
    print("\n🔄 CONTENT EXPANSION")
    print("="*50)
    print("Your world is ready to play! Would you like to expand any sections?")
    print("Expansion adds detailed lore, NPCs, and connections.")
    
    choice = inquirer.select(
        message="Expand world content?",
        choices=[
            "🚀 Yes - Expand all sections (2-3 minutes)",
            "🎯 Selective - Choose which sections to expand",
            "⏩ No - Use base content (ready to play now)"
        ]
    ).execute()
    
    if "🚀 Yes" in choice:
        return True
    elif "🎯 Selective" in choice:
        return offer_selective_expansion()
    else:
        return False

def offer_selective_expansion() -> bool:
    """Let user choose which sections to expand"""
    from InquirerPy import inquirer
    
    expansion_choices = inquirer.checkbox(
        message="Which sections would you like to expand?",
        choices=[
            {"name": "🏛️ Pantheon - Detailed religions, temples, clergy", "value": "pantheon"},
            {"name": "✨ Magic System - Schools, spells, limitations", "value": "magic_system"}, 
            {"name": "👹 Global Threats - Detailed villains, minions", "value": "global_threats"},
            {"name": "🌍 World Overview - History, cultures, politics", "value": "world_overview"}
        ]
    ).execute()
    
    # Store selected expansions for later use
    global selected_expansions
    selected_expansions = expansion_choices
    
    return len(expansion_choices) > 0

def expand_world_content(campaign_id: str, world_id: str, auto_expand: bool = False):
    """
    Expand world content using expansion bots
    
    Args:
        campaign_id: Campaign UUID
        world_id: World UUID  
        auto_expand: If True, expand all sections automatically
    """
    # TODO: Implement expansion bots
    print("🚧 Content expansion bots coming soon!")
    
    if auto_expand:
        print("   🏛️ Expanding pantheon...")
        print("   ✨ Expanding magic system...")
        print("   👹 Expanding global threats...")
        print("   ✅ Auto-expansion complete!")
    else:
        global selected_expansions
        for section in selected_expansions:
            print(f"   🔄 Expanding {section}...")
        print("   ✅ Selected expansions complete!")

# Global variable to store user expansion choices
selected_expansions = []

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

def delete_campaign_from_database(campaign_id):
    """Delete a campaign and all associated data from the database"""
    from db.db import get_db_connection
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Delete the campaign - CASCADE DELETE will handle all associated data
        cur.execute("DELETE FROM campaigns WHERE campaign_id = %s", (campaign_id,))
        
        # Check if any rows were affected
        if cur.rowcount == 0:
            print("❌ Campaign not found in database!")
            return False
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

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
                run_game_session(game_session, is_new_character=True)
                
        elif choice == "🔴 Load Existing Character":
            # Load existing character (only available for existing campaigns)
            game_session = load_existing_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session, is_new_character=False)
                
        elif choice == "Create New Character":
            # Create new character for existing campaign
            game_session = create_new_character(campaign_id, username)
            if game_session:
                # Update campaign last played time
                campaign_manager.update_last_played(campaign_id)
                run_game_session(game_session)
                
        elif choice == "Back to Main Menu":
            return campaign_menu()  # Back to main menu

def run_game_session(game_session, is_new_character=False):
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
