# cli.py
import typer
from InquirerPy import inquirer
from debug.debug_util import debug_log
from services import character_creator
from utils.dice_utility import DiceUtility

dice = DiceUtility()
app = typer.Typer()

def create_auto_choice(text):
    """Create a distinctive 'decide for me' choice option"""
    return f"🎲 Decide for me: {text}"

def is_auto_choice(choice):
    """Check if user selected a 'decide for me' option"""
    return choice.startswith("🎲 AUTO:")

def ui_main_menu():
    choice = inquirer.select(
        message="Welcome to Agentic Dungeon Master! Choose an option:",
        choices=[
            "Play",
            "Start New Campaign",
            "Load Previous Campaign",
            "Options",
            "Quit"
        ]
    ).execute()
    return choice

def ui_options_menu():
    """Options and settings menu"""
    choice = inquirer.select(
        message="⚙️ Options & Settings - Choose an option:",
        choices=[
            "🌍 World Builder",
            "🗑️ Delete Campaign",
            "⚙️ Game Settings (coming soon)",
            "🔧 Debug Tools (coming soon)",
            "🔙 Back to Main Menu"
        ]
    ).execute()
    return choice

def ui_character_menu_new_campaign():
    """Character selection menu for new campaigns"""
    choice = inquirer.select(
        message="New Campaign - Choose an option:",
        choices=[
            "🔴 Create New Character",
            "Back to Main Menu"
        ]
    ).execute()
    return choice

def ui_character_menu_existing_campaign():
    """Character selection menu for existing campaigns"""
    choice = inquirer.select(
        message="Campaign Session - Choose an option:",
        choices=[
            "🔴 Load Existing Character",
            "Create New Character",
            "Back to Main Menu"
        ]
    ).execute()
    return choice

def ui_quit():
    typer.echo("Goodbye!")
    raise typer.Exit()

def ui_start_new_campaign():
    debug_log("ui_start_new_campaign() called.")
    typer.secho("\n🛡️ Starting a New Campaign...", fg=typer.colors.GREEN)

def ui_get_char_name():
    return input("Enter your character's name: ")

def ui_get_char_class():
    return inquirer.select(
        message="Select your class:",
        choices=character_creator.class_options
    ).execute()

def ui_setup_character():
    debug_log("ui_setup_character() called.")
    typer.secho("\n🧙 Choose your character:", fg=typer.colors.MAGENTA)
    char_class = ui_get_char_class()
    name = ui_get_char_name()
    return name, char_class

def ui_intro_text():
    typer.secho("\n🎮 Welcome to your adventure!", fg=typer.colors.GREEN)

def ui_combat_over():
    typer.secho("\nCombat is over. Back to the story...", fg=typer.colors.BRIGHT_BLUE)

def ui_character_sheet():
    """Legacy function - now displays message about using in-game commands"""
    typer.secho("\n📜 Character Sheet:", fg=typer.colors.CYAN)
    typer.echo("Use the 'debug' command during gameplay to see character stats!")

def ui_player_character_sheet(character):
    """Display character sheet from game session data"""
    if not character:
        typer.echo("No character data available!")
        return
        
    typer.secho("\n📜 Character Sheet:", fg=typer.colors.CYAN)
    typer.echo(f"Name: {character.get('name', 'Unknown')}")
    typer.echo(f"Class: {character.get('class', 'Unknown')}")
    typer.echo(f"Level: {character.get('level', 1)}")
    typer.echo(f"Experience: {character.get('experience', 0)}")
    typer.echo(f"HP: {character.get('hp', 0)}/{character.get('max_hp', 0)}")
    typer.echo(f"AC: {character.get('ac', 10)}")
    typer.echo(f"STR: {character.get('strength', 10)}  DEX: {character.get('dexterity', 10)}  CON: {character.get('constitution', 10)}")
    typer.echo(f"INT: {character.get('intelligence', 10)}  WIS: {character.get('wisdom', 10)}  CHA: {character.get('charisma', 10)}")

def ui_player_choice():
    choice = inquirer.select(
        message="Choose an option:",
        choices=[
            "Type an Action",
            "Character Sheet",
            "Inventory (placeholder)",
            "Journal (placeholder)",
            "Debug Menu",
            "Return to Start Menu",
            "Quit Application"
        ]
    ).execute()
    return choice

def ui_get_action():
    return input("\nWhat do you do? ")

def ui_display_dm_narration(text):
    typer.secho("\n🪄 The Dungeon Master says:", fg=typer.colors.BRIGHT_BLUE)
    typer.echo(text)
    typer.echo("")

def ui_handle_dice_roll(roll_info, dice_result):
    typer.secho(f"\n  🎲 {roll_info['roll_type']} is required. DC {roll_info['dc']}", fg=typer.colors.YELLOW)
    choice = inquirer.select(
        message="Choose an option:",
        choices=["Roll!"]
    ).execute()

    if choice == "Roll!":
        typer.secho(f"You rolled a {dice_result} on a {roll_info['dice_type']}", fg=typer.colors.BRIGHT_YELLOW)
        typer.echo("")
    else:
        typer.echo("No roll made.")
        return None

def ui_declare_dice_result(success):
    typer.secho(f"\n {success}", fg=typer.colors.BRIGHT_YELLOW)

def ui_show_roll(name, roll):
    print(f"{name} rolled a {roll}!")

def ui_show_damage(name, damage, success):
    if success:
        print(f"{name} hits for {damage} damage!")
    else:
        print(f"{name} misses their attack!")

# ========================================
# LEAN CLI FUNCTIONS FOR ALL SCATTERED PRINTS
# ========================================

def ui_header(title, width=50):
    """Display a formatted header with title"""
    typer.echo("\n" + "="*width)
    typer.echo(title)
    typer.echo("="*width)

def ui_section_header(title):
    """Display a section header"""
    typer.echo(f"\n{title}:")

def ui_menu_options(options_list):
    """Display numbered menu options"""
    for i, option in enumerate(options_list, 1):
        typer.echo(f"{i}. {option}")

def ui_info_message(message):
    """Display an informational message"""
    typer.echo(message)

def ui_status_message(message):
    """Display a status message"""
    typer.echo(message)

def ui_error_message(message):
    """Display an error message"""
    typer.echo(message)

def ui_list_item(text, indent=0):
    """Display a list item with optional indentation"""
    spacing = "   " * indent
    typer.echo(f"{spacing}{text}")

def ui_debug_message(message):
    """Display a debug message (uses print for debugging)"""
    print(message)

def ui_combat_message(message):
    """Display combat-related message"""
    typer.echo(message)

def ui_help_text():
    """Display available commands help"""
    typer.echo("\n🎮 AVAILABLE COMMANDS:")
    typer.echo("Debug Commands:")
    typer.echo("  god     - God mode (999 HP, 25 AC)")
    typer.echo("  heal    - Full heal")
    typer.echo("  win     - Kill all enemies (combat only)")
    typer.echo("  debug   - Show debug info")
    typer.echo("  menu    - Return to menu")
    typer.echo("\n🧠 AI Memory Commands:")
    typer.echo("  memory       - View recent story events")
    typer.echo("  relationships - View NPC relationships")
    typer.echo("  npcs         - View NPCs at current location")
    typer.echo("  location     - View current location")
    typer.echo("  help         - Show this help")
    typer.echo("\nType any command during story or combat!")

def ui_memory_display(events):
    """Display memory events"""
    if not events:
        typer.echo("   No events recorded yet.")
        return
        
    for i, event in enumerate(events, 1):
        timestamp = event['created_at'].strftime("%H:%M:%S") if event['created_at'] else "Unknown"
        typer.echo(f"\n{i}. [{timestamp}] {event['event_type'].upper()}")
        typer.echo(f"   Location: {event['location'] or 'Unknown'}")
        typer.echo(f"   Event: {event['description'][:100]}{'...' if len(event['description']) > 100 else ''}")
        if event['player_actions']:
            typer.echo(f"   Player: {event['player_actions'][:80]}{'...' if len(event['player_actions']) > 80 else ''}")

def ui_relationships_display(player_name, relationships):
    """Display NPC relationships"""
    typer.echo(f"\n🤝 NPC RELATIONSHIPS for {player_name}:")
    
    if not relationships:
        typer.echo("   No relationships established yet.")
        return
        
    for rel in relationships:
        score = rel['relationship_score']
        
        # Determine relationship status
        if score > 50:
            status = "🟢 Strong Ally"
        elif score > 20:
            status = "🔵 Ally"
        elif score > -20:
            status = "⚪ Neutral"
        elif score > -50:
            status = "🔴 Enemy"
        else:
            status = "🔴 Strong Enemy"
            
        typer.echo(f"\n• {rel['npc_name']} - {status} ({score:+d})")
        if rel['last_interaction']:
            typer.echo(f"  Last: {rel['last_interaction'][:100]}{'...' if len(rel['last_interaction']) > 100 else ''}")
        
        # Show relationship history if available
        if rel['history'] and len(rel['history'].strip()) > 0:
            history_lines = rel['history'].split('\n')[-2:]  # Last 2 interactions
            for line in history_lines:
                if line.strip():
                    typer.echo(f"  History: {line.strip()[:80]}{'...' if len(line.strip()) > 80 else ''}")

def ui_npcs_display(location, npcs):
    """Display NPCs at location"""
    typer.echo(f"\n👥 NPCs AT {location.upper()}:")
    
    if not npcs:
        typer.echo("   No living NPCs at this location.")
        return
        
    for npc in npcs:
        disposition_emoji = {
            "friendly": "😊",
            "hostile": "😠", 
            "neutral": "😐",
            "unknown": "❓"
        }.get(npc.get('disposition', 'neutral'), "😐")
        
        typer.echo(f"\n• {npc['name']} ({npc['class']}) {disposition_emoji}")
        typer.echo(f"  HP: {npc['hp']}/{npc.get('max_hp', npc['hp'])} | AC: {npc['ac']} | Status: {npc['status']}")
        if npc.get('backstory'):
            typer.echo(f"  Background: {npc['backstory'][:100]}{'...' if len(npc['backstory']) > 100 else ''}")
        
        last_seen = npc.get('last_seen')
        if last_seen:
            typer.echo(f"  Last seen: {last_seen.strftime('%Y-%m-%d %H:%M:%S') if hasattr(last_seen, 'strftime') else last_seen}")

def ui_location_display(location, living_npcs_count, dead_npcs_count=0, recent_events_count=0, latest_event=None):
    """Display location information"""
    typer.echo(f"\n📍 CURRENT LOCATION: {location}")
    typer.echo(f"   Living NPCs: {living_npcs_count}")
    if dead_npcs_count:
        typer.echo(f"   Dead NPCs: {dead_npcs_count}")
    if recent_events_count:
        typer.echo(f"   Recent events here: {recent_events_count}")
    if latest_event:
        typer.echo(f"   Latest: {latest_event['event_type']} - {latest_event['description'][:80]}{'...' if len(latest_event['description']) > 80 else ''}")

def ui_get_input(prompt):
    """Get input from user with prompt"""
    return input(prompt)

def ui_campaign_list(campaigns):
    """Display list of campaigns"""
    typer.echo("\nYOUR CAMPAIGNS:")
    for i, campaign in enumerate(campaigns, 1):
        campaign_id, name, description, created_at, last_played, creator, role = campaign
        last_played_str = last_played.strftime("%Y-%m-%d %H:%M") if last_played else "Never"
        typer.echo(f"{i}. {name} ({role}) - Last played: {last_played_str}")
        if description:
            typer.echo(f"   Description: {description}")

def ui_initiative_display(combatants_initiative):
    """Display initiative order"""
    typer.echo("\nInitiative Order:")
    for c in combatants_initiative:
        typer.echo(f"  {c['name']}: {c['initiative']}")

def ui_combatant_status(combatants):
    """Display combatant status"""
    typer.echo("\n-- Combatant Status --")
    for name, stats in combatants.items():
        typer.echo(f"  {name}: {stats['hp']} HP")

class WorldBuilderCLI:
    """CLI interface for world building functionality"""
    
    def show_world_builder_menu(self):
        """Main world builder menu"""
        while True:
            choice = inquirer.select(
                message="🌍 World Builder - Choose an option:",
                choices=[
                    "🆕 Generate New World",
                    "🌌 Generate Universe Only (Test Save-Down)",
                    "🏰 Generate Test Settlement (Oakwood Village)",
                    "👥 Generate NPC Network", 
                    "⚔️ Generate Conflict Web",
                    "📜 Generate Quest Network",
                    "🔍 Analyze Existing World Data",
                    "🗄️ View World Database",
                    "🧪 Run World Builder Tests",
                    "🔙 Back to Main Menu"
                ]
            ).execute()
            
            if choice == "🆕 Generate New World":
                self.handle_generate_new_world()
            elif choice == "🌌 Generate Universe Only (Test Save-Down)":
                self.handle_generate_universe_only()
            elif choice == "🏰 Generate Test Settlement (Oakwood Village)":
                self.handle_generate_test_settlement()
            elif choice == "👥 Generate NPC Network":
                self.handle_generate_npc_network()
            elif choice == "⚔️ Generate Conflict Web":
                self.handle_generate_conflict_web()
            elif choice == "📜 Generate Quest Network":
                self.handle_generate_quest_network()
            elif choice == "🔍 Analyze Existing World Data":
                self.handle_analyze_world_data()
            elif choice == "🗄️ View World Database":
                self.handle_view_world_database()
            elif choice == "🧪 Run World Builder Tests":
                self.handle_run_tests()
            elif choice == "🔙 Back to Main Menu":
                break

    def handle_generate_new_world(self):
        """Handle full world generation with campaign and world choice"""
        typer.secho("\n🌍 WORLD GENERATION WIZARD", fg=typer.colors.CYAN, bold=True)
        
        while True:
            # Get campaign selection
            campaign_id = self.get_campaign_selection()
            if not campaign_id:
                return
                
            # Get world choice for this campaign
            campaign_id, world_choice = self.get_world_choice_for_campaign(campaign_id)
            
            if world_choice == "back":
                continue  # Go back to campaign selection
            elif world_choice == "new_world":
                break  # Proceed with world generation
            else:
                return  # Exit
        
        # Get world parameters
        typer.echo()
        typer.secho("🏗️ Let's build your world!", fg=typer.colors.GREEN, bold=True)
        world_params = self.get_world_parameters()
        
        # Call world builder orchestrator
        from world_builder import WorldGenerationOrchestrator
        orchestrator = WorldGenerationOrchestrator()
        
        typer.echo("🔄 Generating complete world... (this may take a moment)")
        result = orchestrator.generate_complete_world(campaign_id, world_params)
        
        if result.success:
            typer.secho(f"✅ World '{result.world_name}' generated successfully!", fg=typer.colors.GREEN)
            typer.secho(f"📁 Saved to campaign: {campaign_id}", fg=typer.colors.BLUE)
            self.display_world_summary(result)
        else:
            typer.secho(f"❌ World generation failed: {result.error}", fg=typer.colors.RED)
        
        input("\n📖 Press Enter to continue...")

    def handle_generate_universe_only(self):
        """Handle universe-only generation for testing save-down functionality"""
        typer.secho("\n🌌 UNIVERSE GENERATOR (Test Save-Down)", fg=typer.colors.CYAN, bold=True)
        
        while True:
            # Get campaign selection
            campaign_id = self.get_campaign_selection()
            if not campaign_id:
                return
                
            # Get world choice for this campaign
            campaign_id, world_choice = self.get_world_choice_for_campaign(campaign_id)
            
            if world_choice == "back":
                continue  # Go back to campaign selection
            elif world_choice == "new_world":
                break  # Proceed with universe generation
            else:
                return  # Exit
        
        # Get world parameters
        typer.echo()
        typer.secho("🏗️ Let's build your universe foundation!", fg=typer.colors.GREEN, bold=True)
        world_params = self.get_world_parameters()
        
        # Call UniverseBuilder directly for testing
        from bots.world_builder.universe_builder import UniverseBuilder
        
        typer.echo("🔄 Generating universe context... (this may take a moment)")
        
        try:
            builder = UniverseBuilder()
            universe_data = builder.generate_universe_context(world_params)
            
            typer.secho(f"✅ Universe '{universe_data.get('world_info', {}).get('world_name', 'Unknown')}' generated!", fg=typer.colors.GREEN)
            typer.secho(f"📁 Campaign: {campaign_id}", fg=typer.colors.BLUE)
            
            # TODO: Add database save functionality here
            typer.secho("💾 Saving to database... (coming soon!)", fg=typer.colors.YELLOW)
            
            # Display basic summary
            world_info = universe_data.get('world_info', {})
            size_info = universe_data.get('size', {})
            magic_info = universe_data.get('magic_system', {})
            
            typer.echo("\n📊 Universe Summary:")
            typer.echo(f"   🌍 World: {world_info.get('world_name', 'Unknown')}")
            typer.echo(f"   📏 Scope: {size_info.get('scope', 'Unknown')}")
            typer.echo(f"   🗺️ Regions: {size_info.get('region_count', 0)}")
            typer.echo(f"   🏙️ Major Cities: {size_info.get('major_city_count', 0)}")  
            typer.echo(f"   🏘️ Settlements: {size_info.get('settlement_count', 0)}")
            typer.echo(f"   ✨ Magic Level: {magic_info.get('magic_level', 'Unknown')}")
            
            pantheon_info = universe_data.get('pantheon', {})
            deities = pantheon_info.get('major_deities', [])
            if deities:
                typer.echo(f"   ⚡ Major Deities: {len(deities)}")
                for deity in deities[:3]:  # Show first 3
                    typer.echo(f"      • {deity}")
                if len(deities) > 3:
                    typer.echo(f"      • ... and {len(deities) - 3} more")
            
            threats = universe_data.get('global_threats', [])
            if threats:
                typer.echo(f"   ⚔️ Global Threats: {len(threats)}")
                for threat in threats:
                    typer.echo(f"      • {threat.get('primary_threat', 'Unknown Threat')}")
                    
        except Exception as e:
            typer.secho(f"❌ Universe generation failed: {str(e)}", fg=typer.colors.RED)
        
        input("\n📖 Press Enter to continue...")

    def handle_generate_test_settlement(self):
        """Handle test settlement generation"""
        typer.secho("\n🏰 GENERATE TEST SETTLEMENT", fg=typer.colors.CYAN, bold=True)
        
        campaign_id = self.get_campaign_selection()
        if not campaign_id:
            return
            
        from world_builder import WorldGenerationOrchestrator
        orchestrator = WorldGenerationOrchestrator()
        
        typer.echo("🔄 Generating Oakwood Village test settlement...")
        result = orchestrator.generate_test_settlement(campaign_id, "Oakwood Village")
        
        if result.success:
            typer.secho("✅ Test settlement generated!", fg=typer.colors.GREEN)
            self.display_settlement_summary(result.settlement_data)
        else:
            typer.secho(f"❌ Generation failed: {result.error}", fg=typer.colors.RED)
            
        input("\n📖 Press Enter to continue...")

    def handle_generate_npc_network(self):
        """Handle NPC network generation"""
        typer.secho("\n👥 GENERATE NPC NETWORK", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 NPC network generation - coming soon!")
        input("\n📖 Press Enter to continue...")

    def handle_generate_conflict_web(self):
        """Handle conflict web generation"""
        typer.secho("\n⚔️ GENERATE CONFLICT WEB", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 Conflict web generation - coming soon!")
        input("\n📖 Press Enter to continue...")

    def handle_generate_quest_network(self):
        """Handle quest network generation"""
        typer.secho("\n📜 GENERATE QUEST NETWORK", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 Quest network generation - coming soon!")
        input("\n📖 Press Enter to continue...")

    def handle_analyze_world_data(self):
        """Handle world data analysis"""
        typer.secho("\n🔍 ANALYZE WORLD DATA", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 World data analysis - coming soon!")
        input("\n📖 Press Enter to continue...")

    def handle_view_world_database(self):
        """Handle viewing world database"""
        typer.secho("\n🗄️ WORLD DATABASE VIEWER", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 Database viewer - coming soon!")
        input("\n📖 Press Enter to continue...")

    def handle_run_tests(self):
        """Handle running world builder tests"""
        typer.secho("\n🧪 WORLD BUILDER TESTS", fg=typer.colors.CYAN, bold=True)
        typer.echo("🚧 Test runner - coming soon!")
        input("\n📖 Press Enter to continue...")

    def get_campaign_selection(self):
        """Get campaign selection from user"""
        typer.secho("\n🎮 CAMPAIGN SETUP", fg=typer.colors.CYAN, bold=True)
        
        # For now, simple input - could be enhanced with campaign browser
        campaign_id = input("\nEnter Campaign ID (or press Enter for test): ").strip()
        if not campaign_id:
            campaign_id = "test_campaign_001"
            typer.echo(f"Using test campaign: {campaign_id}")
        return campaign_id
    
    def get_world_choice_for_campaign(self, campaign_id):
        """Ask user whether to create new world or use existing world for this campaign"""
        typer.echo()
        typer.secho("🌍 WORLD SELECTION", fg=typer.colors.CYAN, bold=True)
        typer.echo(f"Campaign: {campaign_id}")
        typer.echo()
        
        import inquirer
        
        world_choice = inquirer.select(
            message="Would you like to:",
            choices=[
                "🆕 Create a new world for this campaign",
                "🏛️ Play in an established world (coming soon)",
                "🔙 Back to campaign selection"
            ]
        ).execute()
        
        if "🔙 Back" in world_choice:
            return None, "back"
        elif "🏛️ Play in an established" in world_choice:
            typer.secho("🚧 Established world selection coming soon!", fg=typer.colors.YELLOW)
            typer.echo("For now, let's create a new world...")
            return campaign_id, "new_world"
        else:
            return campaign_id, "new_world"

    def get_world_parameters(self):
        """Get world generation parameters from user with conversational approach"""
        typer.echo("\n" + "="*60)
        typer.secho("🌟 WORLD ARCHITECT CONSULTATION 🌟", fg=typer.colors.CYAN, bold=True)
        typer.echo("="*60)
        typer.echo()
        typer.secho("Greetings, Creator! I am your World Architect, ready to help you", fg=typer.colors.BRIGHT_BLUE)
        typer.secho("craft a living, breathing world for your adventures.", fg=typer.colors.BRIGHT_BLUE)
        typer.echo()
        typer.secho("Let's have a conversation about the world you envision...", fg=typer.colors.BRIGHT_BLUE)
        typer.echo()
        
        # World Scale and Scope (FIRST - this informs everything else)
        typer.secho("🗺️ First, let's establish the scope of your world...", fg=typer.colors.BRIGHT_BLUE)
        
        size = inquirer.select(
            message="How vast is this realm you're creating?",
            choices=[
                create_auto_choice("Surprise me with the perfect scope!"),
                "Intimate - Single kingdom (1 region, 1 major city, 5-8 settlements)",
                "Regional - Small continent (3 kingdoms, 3-5 major cities, 15-20 settlements)", 
                "Continental - Vast lands (5+ kingdoms, 8+ major cities, 30+ settlements)",
                "Wilderness - Untamed lands (3 regions, 0-1 cities, 2-5 outposts/camps)",
                "Custom - I'll describe my vision"
            ]
        ).execute()
        
        # Custom size input
        if "Custom" in size:
            typer.echo()
            custom_size = input("💭 Describe your world's scope and scale: ").strip()
            if custom_size:
                size = f"Custom: {custom_size}"
        
        # Theme and Genre
        typer.echo()
        theme = inquirer.select(
            message="🎭 What kind of story does this world tell?",
            choices=[
                create_auto_choice("Create something amazing!"),
                "High Fantasy - Magic is everywhere, heroes are legendary",
                "Low Fantasy - Magic is rare and mysterious", 
                "Dark Fantasy - Magic comes with terrible prices",
                "Steampunk - Magic meets clockwork and steam",
                "Sword & Sorcery - Gritty adventures and primal magic",
                "Urban Fantasy - Modern world with hidden magic",
                "Post-Apocalyptic Fantasy - Magic survived the end times",
                "🔧 Custom - I have something unique in mind"
            ]
        ).execute()
        
        # Custom theme input
        if "🔧 Custom" in theme:
            typer.echo()
            custom_theme = input("💭 Describe your unique story theme or genre: ").strip()
            if custom_theme:
                theme = f"Custom: {custom_theme}"
        
        # Magic System (UPDATED with forbidden options)
        typer.echo()
        typer.secho("✨ Now, let's talk about the mystical forces in your world...", fg=typer.colors.BRIGHT_BLUE)
        
        magic_commonality = inquirer.select(
            message="How common is magic in everyday life?",
            choices=[
                create_auto_choice("You pick what fits!"),
                "Everywhere - Even farmers use cantrips for crops",
                "Common - Most towns have a wizard or healer", 
                "Uncommon - Magic users are known but special",
                "Rare - Magic is whispered about in legends",
                "Forbidden Everywhere - Magic is outlawed across all lands",
                "Forbidden Someplace - Magic laws vary by region", 
                "Dying - Magic is fading from the world",
                "🔧 Custom - Let me explain my vision"
            ]
        ).execute()
        
        # Custom magic input
        if "🔧 Custom" in magic_commonality:
            typer.echo()
            custom_magic = input("💭 Describe how magic works in your world: ").strip()
            if custom_magic:
                magic_commonality = f"Custom: {custom_magic}"
        
        # Deities and Religion
        typer.echo()
        typer.secho("⚡ What about the divine? Who watches over this world?", fg=typer.colors.BRIGHT_BLUE)
        
        deity_structure = inquirer.select(
            message="What is the religious landscape like?",
            choices=[
                create_auto_choice("Build me a pantheon!"),
                "Pantheon - Many gods, many religions competing",
                "Monotheistic - One dominant religion, one supreme deity",
                "Dualistic - Good vs Evil, Light vs Dark eternal struggle", 
                "Ancestor Worship - The dead guide the living",
                "Nature Spirits - Rivers, trees, mountains have souls",
                "Dead Gods - The divine once lived, now only echoes remain",
                "No Gods - Mortals make their own destiny",
                "Hidden Gods - Divine beings exist but rarely interfere",
                "🔧 Custom - I have a unique divine structure"
            ]
        ).execute()
        
        # Custom deity input
        if "🔧 Custom" in deity_structure:
            typer.echo()
            custom_deity = input("💭 Describe your unique religious or divine structure: ").strip()
            if custom_deity:
                deity_structure = f"Custom: {custom_deity}"
        
        # Major Global Threats (REWORKED to support multiple threats)
        typer.echo()
        typer.secho("⚔️ What GLOBAL threats loom over this world?", fg=typer.colors.BRIGHT_BLUE)
        typer.secho("(Regional conflicts will be generated separately)", fg=typer.colors.YELLOW)
        
        threat_choice = inquirer.select(
            message="What world-spanning dangers exist?",
            choices=[
                create_auto_choice("Craft an epic threat!"),
                "Ancient Evil - Something terrible stirs from long slumber",
                "Planar Invasion - Outsiders from other realms threaten reality", 
                "Divine War - Gods themselves clash, mortals suffer",
                "World-Ending Catastrophe - The very planet is in upheaval",
                "Cosmic Horror - Things beyond understanding encroach",
                "None Yet - Let threats emerge through play",
                "⚔️ Multiple Threats - This world faces several global dangers",
                "🔧 Custom - I have specific global conflicts in mind"
            ]
        ).execute()
        
        # Handle multiple threats or single threat
        global_threats = []
        if "⚔️ Multiple Threats" in threat_choice:
            global_threats = self._collect_multiple_threats()
        elif "🔧 Custom" in threat_choice:
            typer.echo()
            custom_threat = input("💭 Describe your specific global conflicts or threats: ").strip()
            if custom_threat:
                global_threats = [f"Custom: {custom_threat}"]
            else:
                global_threats = ["None Yet - Let threats emerge through play"]
        else:
            global_threats = [threat_choice]
        
                # Custom Details (UPDATED with choice)
        typer.echo()
        typer.secho("📝 Finally, do you have any special details or inspirations", fg=typer.colors.BRIGHT_BLUE)
        typer.secho("that would help me craft this world perfectly for you?", fg=typer.colors.BRIGHT_BLUE)
        
        has_custom_ideas = inquirer.select(
            message="Any unique elements you'd like to share?",
            choices=[
                "No, I'm excited to see what you come up with!",
                "Yes, I have a few ideas I'd like to share"
            ]
        ).execute()
        
        custom_details = ""
        if "Yes" in has_custom_ideas:
            custom_details = input("\n💭 Share your inspirations, must-have elements, or special details: ").strip()

        # World Name Choice
        typer.echo()
        typer.secho("🌍 What should we call this world?", fg=typer.colors.BRIGHT_BLUE)
        
        name_choice = inquirer.select(
            message="How should we name your world?",
            choices=[
                "🎲 Let the AI create an evocative name",
                "📝 I want to name it myself"
            ]
        ).execute()
        
        world_name = ""
        if "📝" in name_choice:
            world_name = input("\n🏷️ What is your world's name? ").strip()
            if world_name:
                typer.echo(f"✨ Perfect! Welcome to {world_name}!")
            else:
                world_name = ""  # Let AI generate if user doesn't provide one

        # Note: Region design will happen as a separate step after world creation


        
        # Final confirmation
        typer.echo()
        typer.secho("🎯 Excellent! I have everything I need to begin crafting your world.", fg=typer.colors.GREEN, bold=True)
        typer.secho("Prepare yourself for something truly special...", fg=typer.colors.GREEN)
        typer.echo()
        
        # TODO: Campaign ID is used for database storage, but we might not need it for world generation
        # Will revisit this when we implement database integration
        
        # Process parameters for the world builder (regions will be handled separately)
        processed_params = {
            "theme": theme,
            "size": size,
            "magic_commonality": magic_commonality,
            "deity_structure": deity_structure,
            "global_threats": global_threats,
            "world_name": world_name,
            "custom_details": custom_details,
            "has_custom_ideas": has_custom_ideas
        }
        
        return processed_params
    
    def _collect_multiple_threats(self):
        """Collect multiple global threats from user"""
        threats = []
        typer.echo()
        typer.secho("🌪️ Multiple Global Threats - Let's define them one by one:", fg=typer.colors.BRIGHT_BLUE)
        
        threat_options = [
            "Ancient Evil - Something terrible stirs from long slumber",
            "Planar Invasion - Outsiders from other realms threaten reality", 
            "Divine War - Gods themselves clash, mortals suffer",
            "World-Ending Catastrophe - The very planet is in upheaval",
            "Cosmic Horror - Things beyond understanding encroach",
            "🔧 Custom threat - I'll describe this one"
        ]
        
        for threat_num in range(1, 6):  # Allow up to 5 threats
            typer.echo()
            if threat_num == 1:
                choice = inquirer.select(
                    message="🎯 First global threat:",
                    choices=threat_options + ["🛑 No more threats needed"]
                ).execute()
            else:
                choice = inquirer.select(
                    message=f"🎯 Global threat #{threat_num} (optional):",
                    choices=threat_options + ["🛑 That's enough threats for now"]
                ).execute()
            
            if "🛑" in choice:
                break
                
            if "🔧 Custom" in choice:
                custom_threat = input(f"💭 Describe global threat #{threat_num}: ").strip()
                if custom_threat:
                    threats.append(f"Custom: {custom_threat}")
            else:
                threats.append(choice)
                
        if not threats:
            threats = ["None Yet - Let threats emerge through play"]
            
        typer.echo()
        typer.secho(f"✅ Configured {len(threats)} global threat(s)", fg=typer.colors.GREEN)
        for i, threat in enumerate(threats, 1):
            typer.secho(f"   {i}. {threat.split(' - ')[0]}", fg=typer.colors.BLUE)
            
        return threats

    
    def _get_region_count_from_size(self, size):
        """Determine number of regions based on world size"""
        if "Intimate" in size:
            return 1
        elif "Regional" in size:
            return 3
        elif "Continental" in size:
            return 5
        elif "Wilderness" in size:
            return 3
        else:  # Custom or auto
            return 3  # Default for auto
    
    def _handle_granular_region_generation(self, region_count, involvement_level):
        """Handle step-by-step region generation with user control at each step"""
        regional_data = []
        
        for region_num in range(1, region_count + 1):
            typer.echo()
            typer.secho(f"🏰 REGION {region_num} of {region_count}", fg=typer.colors.CYAN, bold=True)
            
            # Ask if user wants to design this region or auto-generate
            if region_num == 1:
                region_choice = inquirer.select(
                    message=f"How should we create Region {region_num}?",
                    choices=[
                        "🖌️ I want to design this region myself",
                        "🎲 Auto-generate this region for me",
                        f"🚀 Auto-generate all {region_count} regions"
                    ]
                ).execute()
            else:
                remaining_regions = region_count - region_num + 1
                region_choice = inquirer.select(
                    message=f"How should we create Region {region_num}?",
                    choices=[
                        "🖌️ I want to design this region myself",
                        "🎲 Auto-generate this region for me",
                        f"🚀 Auto-generate all {remaining_regions} remaining regions"
                    ]
                ).execute()
            
            if "Auto-generate all" in region_choice:
                # Auto-generate all remaining regions
                for auto_region_num in range(region_num, region_count + 1):
                    regional_data.append({
                        'name': f'AUTO_REGION_{auto_region_num}',
                        'type': 'auto',
                        'political_system': 'auto', 
                        'regional_conflict': 'auto',
                        'settlements': 'auto',
                        'landmarks': 'auto'
                    })
                break
                
            elif "Auto-generate this region" in region_choice:
                # Auto-generate just this region
                regional_data.append({
                    'name': f'AUTO_REGION_{region_num}',
                    'type': 'auto',
                    'political_system': 'auto',
                    'regional_conflict': 'auto',
                    'settlements': 'auto',
                    'landmarks': 'auto'
                })
                
            else:
                # User wants to design this region
                regional_params = self.get_regional_parameters(region_num, involvement_level)
                
                # Ask about settlements for this region
                typer.echo()
                typer.secho(f"🏘️ Now let's handle settlements in {regional_params['name']}", fg=typer.colors.BRIGHT_YELLOW)
                
                settlement_data = self._handle_granular_settlement_generation(regional_params, involvement_level)
                regional_params['settlements'] = settlement_data
                
                # Ask about landmarks/geographical features for this region
                typer.echo()
                typer.secho(f"🏔️ Now let's add landmarks and geographical features to {regional_params['name']}", fg=typer.colors.BRIGHT_CYAN)
                
                landmark_data = self._handle_granular_landmark_generation(regional_params, involvement_level)
                regional_params['landmarks'] = landmark_data
                
                regional_data.append(regional_params)
        
        return regional_data
    
    def _handle_granular_settlement_generation(self, regional_params, involvement_level):
        """Handle step-by-step settlement generation with user control at each step"""
        region_name = regional_params['name']
        
        # Determine settlement count based on region size/type
        settlement_count = self._get_settlement_count_from_region(regional_params)
        typer.echo(f"Based on this region, we'll create {settlement_count} settlements.")
        
        settlement_data = []
        
        for settlement_num in range(1, settlement_count + 1):
            typer.echo()
            typer.secho(f"🏘️ SETTLEMENT {settlement_num} of {settlement_count} in {region_name}", fg=typer.colors.YELLOW, bold=True)
            
            # Ask if user wants to design this settlement or auto-generate
            if settlement_num == 1:
                settlement_choice = inquirer.select(
                    message=f"How should we create Settlement {settlement_num}?",
                    choices=[
                        "🖌️ I want to design this settlement myself",
                        "🎲 Auto-generate this settlement for me",
                        f"🚀 Auto-generate all {settlement_count} settlements"
                    ]
                ).execute()
            else:
                remaining_settlements = settlement_count - settlement_num + 1
                settlement_choice = inquirer.select(
                    message=f"How should we create Settlement {settlement_num}?",
                    choices=[
                        "🖌️ I want to design this settlement myself",
                        "🎲 Auto-generate this settlement for me",
                        f"🚀 Auto-generate all {remaining_settlements} remaining settlements"
                    ]
                ).execute()
            
            if "Auto-generate all" in settlement_choice:
                # Auto-generate all remaining settlements
                for auto_settlement_num in range(settlement_num, settlement_count + 1):
                    settlement_data.append({
                        'name': f'AUTO_SETTLEMENT_{auto_settlement_num}',
                        'type': 'auto',
                        'size': 'auto',
                        'economy': 'auto',
                        'notable_features': 'auto',
                        'local_conflict': 'auto'
                    })
                break
                
            elif "Auto-generate this settlement" in settlement_choice:
                # Auto-generate just this settlement
                settlement_data.append({
                    'name': f'AUTO_SETTLEMENT_{settlement_num}',
                    'type': 'auto',
                    'size': 'auto',
                    'economy': 'auto',
                    'notable_features': 'auto',
                    'local_conflict': 'auto'
                })
                
            else:
                # User wants to design this settlement
                settlement_params = self.get_settlement_parameters(settlement_num, regional_params, involvement_level)
                settlement_data.append(settlement_params)
        
        # If there's a formal government and multiple settlements, ask about capital
        political_system = regional_params.get('political_system', '')
        if not ('Wilderness' in political_system or 'Anarchy' in political_system) and len(settlement_data) > 1:
            typer.echo()
            typer.secho("👑 Does any of these settlements serve as the capital/seat of power?", fg=typer.colors.BRIGHT_MAGENTA)
            
            # Create list of settlement names for selection
            settlement_choices = []
            for settlement in settlement_data:
                if settlement.get('name') and settlement['name'] != 'auto':
                    settlement_choices.append(settlement['name'])
                else:
                    settlement_choices.append(f"Settlement {settlement_data.index(settlement) + 1}")
            
            if settlement_choices:
                capital_choice = inquirer.select(
                    message="Which settlement is the capital?",
                    choices=settlement_choices + [
                        "No capital - Power is distributed/shared",
                        create_auto_choice("Let me decide the capital!")
                    ]
                ).execute()
                
                # Mark the chosen settlement as capital
                if not is_auto_choice(capital_choice) and "No capital" not in capital_choice:
                    for settlement in settlement_data:
                        settlement_name = settlement.get('name', f"Settlement {settlement_data.index(settlement) + 1}")
                        if settlement_name == capital_choice:
                            settlement['is_capital'] = True
                        else:
                            settlement['is_capital'] = False
                elif "No capital" in capital_choice:
                    # Mark all settlements as non-capital
                    for settlement in settlement_data:
                        settlement['is_capital'] = False
        
        return settlement_data
    
    def _handle_granular_landmark_generation(self, regional_params, involvement_level):
        """Handle step-by-step landmark/geographical feature generation"""
        region_name = regional_params['name']
        
        # Determine landmark count based on region size/type
        landmark_count = self._get_landmark_count_from_region(regional_params)
        typer.echo(f"Based on this region, we'll create {landmark_count} notable landmarks/features.")
        
        landmark_data = []
        
        for landmark_num in range(1, landmark_count + 1):
            typer.echo()
            typer.secho(f"🏔️ LANDMARK {landmark_num} of {landmark_count} in {region_name}", fg=typer.colors.CYAN, bold=True)
            
            # Ask if user wants to design this landmark or auto-generate
            if landmark_num == 1:
                landmark_choice = inquirer.select(
                    message=f"How should we create Landmark {landmark_num}?",
                    choices=[
                        "🖌️ I want to design this landmark myself",
                        "🎲 Auto-generate this landmark for me",
                        f"🚀 Auto-generate all {landmark_count} landmarks"
                    ]
                ).execute()
            else:
                remaining_landmarks = landmark_count - landmark_num + 1
                landmark_choice = inquirer.select(
                    message=f"How should we create Landmark {landmark_num}?",
                    choices=[
                        "🖌️ I want to design this landmark myself",
                        "🎲 Auto-generate this landmark for me",
                        f"🚀 Auto-generate all {remaining_landmarks} remaining landmarks"
                    ]
                ).execute()
            
            if "Auto-generate all" in landmark_choice:
                # Auto-generate all remaining landmarks
                for auto_landmark_num in range(landmark_num, landmark_count + 1):
                    landmark_data.append({
                        'name': f'AUTO_LANDMARK_{auto_landmark_num}',
                        'type': 'auto',
                        'description': 'auto',
                        'significance': 'auto',
                        'dangers': 'auto'
                    })
                break
                
            elif "Auto-generate this landmark" in landmark_choice:
                # Auto-generate just this landmark
                landmark_data.append({
                    'name': f'AUTO_LANDMARK_{landmark_num}',
                    'type': 'auto',
                    'description': 'auto',
                    'significance': 'auto',
                    'dangers': 'auto'
                })
                
            else:
                # User wants to design this landmark
                landmark_params = self.get_landmark_parameters(landmark_num, regional_params, involvement_level)
                landmark_data.append(landmark_params)
        
        return landmark_data
    
    def _get_landmark_count_from_region(self, regional_params):
        """Determine number of landmarks based on region characteristics"""
        # Simple logic for now - could be more sophisticated
        region_type = regional_params.get('type', '')
        if 'Mountains' in region_type or 'Coast' in region_type:
            return 3  # Dramatic terrain has more landmarks
        elif 'Wilderness' in regional_params.get('political_system', ''):
            return 4  # Wild areas have lots of natural features
        elif 'Plains' in region_type:
            return 2  # Flatter areas have fewer natural landmarks
        else:
            return 3  # Default
    
    def get_landmark_parameters(self, landmark_num, regional_params, involvement_level):
        """Get parameters for a specific landmark"""
        region_name = regional_params['name']
        typer.echo(f"🏔️ Designing Landmark {landmark_num} in {region_name}...")
        
        # Landmark Type
        landmark_type = inquirer.select(
            message="What type of landmark is this?",
            choices=[
                create_auto_choice("Choose perfect type for me!"),
                "Natural Wonder - Mountain, waterfall, canyon, etc.",
                "Ancient Ruins - Old castle, temple, or city",
                "Mysterious Site - Standing stones, crystal formation, etc.",
                "Battlefield - Historic site of conflict",
                "Monument - Statue, tomb, or memorial",
                "Dangerous Location - Dragon lair, cursed forest, etc.",
                "Resource Site - Mine, quarry, magical spring",
                "Crossroads - Important travel junction",
                "Religious Site - Sacred grove, shrine, holy mountain",
                "🔧 Custom - I have something unique in mind"
            ]
        ).execute()
        
        # Significance
        significance = inquirer.select(
            message="What makes this landmark important?",
            choices=[
                create_auto_choice("Build me significance!"),
                "Historical - Site of important events",
                "Religious - Sacred or spiritual importance",
                "Strategic - Military or political value",
                "Economic - Source of wealth or trade",
                "Magical - Arcane properties or phenomena",
                "Cultural - Artistic or social significance",
                "Geographic - Navigation landmark or border",
                "None - Just a notable feature",
                "🔧 Custom - Specific importance"
            ]
        ).execute()
        
        # Potential Dangers/Challenges (optional, only for DESIGNER level)
        dangers = ""
        if "DESIGNER" in involvement_level:
            typer.echo("⚠️ Any dangers or challenges at this landmark?")
            
            danger_choice = inquirer.select(
                message="What risks might adventurers face here?",
                choices=[
                    create_auto_choice("Create appropriate dangers!"),
                    "Monsters - Dangerous creatures live here",
                    "Environmental - Natural hazards like cliffs or weather",
                    "Magical - Arcane traps or unstable magic",
                    "Political - Contested territory or forbidden area", 
                    "Cursed - Dark magic or ancient curse",
                    "Bandits - Criminals use this as hideout",
                    "Unstable - Collapsing ruins or geological hazard",
                    "None - This landmark is safe",
                    "🔧 Custom - Specific dangers"
                ]
            ).execute()
            
            if "Custom" in danger_choice:
                custom_dangers = input("\n⚠️ Describe the dangers: ").strip()
                dangers = f"Custom: {custom_dangers}"
            else:
                dangers = danger_choice
        
        # Ask for landmark name after it's built
        typer.echo()
        typer.secho("🏷️ Now that we've designed this landmark, what should we call it?", fg=typer.colors.BRIGHT_BLUE)
        landmark_name = input(f"📍 Landmark name (or press Enter for auto-name): ").strip()
        if not landmark_name:
            landmark_name = f"AUTO_LANDMARK_{landmark_num}"
        
        # Brief description (optional)
        description = ""
        if "DESIGNER" in involvement_level:
            description = input(f"\n📝 Brief description of {landmark_name} (optional): ").strip()
        
        return {
            'name': landmark_name,
            'type': landmark_type,
            'significance': significance,
            'description': description,
            'dangers': dangers
        }
    
    def _get_settlement_count_from_region(self, regional_params):
        """Determine number of settlements based on region characteristics"""
        # Simple logic for now - could be more sophisticated
        region_type = regional_params.get('type', '')
        if 'Civilized' in region_type or 'City-States' in regional_params.get('political_system', ''):
            return 4  # More urban areas
        elif 'Desert' in region_type or 'Tundra' in region_type:
            return 2  # Harsh environments have fewer settlements
        else:
            return 3  # Default
    
    def get_settlement_parameters(self, settlement_num, regional_params, involvement_level):
        """Get parameters for a specific settlement"""
        region_name = regional_params['name']
        typer.echo(f"🏘️ Designing Settlement {settlement_num} in {region_name}...")
        
        # Settlement Type/Purpose
        settlement_type = inquirer.select(
            message="What type of settlement is this?",
            choices=[
                create_auto_choice("Choose perfect type for me!"),
                "City - Large population, major trade hub",
                "Town - Moderate size, regional importance",
                "Village - Small, rural community",
                "Trading Post - Commercial crossroads",
                "Military Outpost - Fortress or garrison",
                "Mining Settlement - Built around resource extraction",
                "Port - Coastal or river trade center",
                "Religious Center - Temple complex or monastery",
                "Academic Hub - University or magical college",
                "🔧 Custom - I have something unique in mind"
            ]
        ).execute()
        
        # Settlement Size
        settlement_size = inquirer.select(
            message="How large is this settlement?",
            choices=[
                create_auto_choice("Perfect size for its purpose!"),
                "Hamlet (0-50 people)",
                "Tiny (50-100 people)",
                "Small (100-500 people)", 
                "Medium (500-2000 people)",
                "Large (2000-5000 people)",
                "Massive (5000+ people)"
            ]
        ).execute()
        
        # Economic Focus
        economy = inquirer.select(
            message="What drives this settlement's economy?",
            choices=[
                create_auto_choice("Build me an economy!"),
                "Agriculture - Farming and livestock",
                "Trade - Commerce and markets",
                "Crafting - Artisans and workshops",
                "Mining - Ore, gems, or stone extraction",
                "Fishing - Coastal or river resources",
                "Military - Garrison pay and supplies",
                "Religious - Pilgrims and donations",
                "Magic - Arcane services and components",
                "🔧 Custom - Unique economic base"
            ]
        ).execute()
        
        # Notable Features (optional, only for DESIGNER level)
        notable_features = ""
        if "DESIGNER" in involvement_level:
            typer.echo("🌟 Any notable features that make this settlement special?")
            
            feature_choice = inquirer.select(
                message="Does this settlement have distinctive features?",
                choices=[
                    create_auto_choice("Create interesting features!"),
                    "Ancient Ruins - Old structures with history",
                    "Natural Wonder - Unique geography or phenomena", 
                    "Famous Landmark - Well-known building or monument",
                    "Magical Anomaly - Arcane effects or phenomena",
                    "Cultural Center - Festivals, arts, or traditions",
                    "Strategic Position - Important location",
                    "None - Just a typical settlement",
                    "🔧 Custom - I have specific features in mind"
                ]
            ).execute()
            
            if "Custom" in feature_choice:
                custom_features = input("\n🌟 Describe the notable features: ").strip()
                notable_features = f"Custom: {custom_features}"
            else:
                notable_features = feature_choice
        
        # Local Conflict/Issues (optional, only for DESIGNER level)
        local_conflict = ""
        if "DESIGNER" in involvement_level:
            typer.echo("⚔️ Any local issues or conflicts in this settlement?")
            
            conflict_choice = inquirer.select(
                message="What local tensions exist?",
                choices=[
                    create_auto_choice("Create appropriate conflict!"),
                    "Political Rivalry - Competing factions or leaders",
                    "Economic Struggle - Trade disputes or poverty",
                    "Social Tension - Class conflict or discrimination", 
                    "Crime Problem - Thieves, gangs, or corruption",
                    "Monster Threat - Local dangerous creatures",
                    "Resource Shortage - Lacking essential supplies",
                    "Religious Dispute - Competing faiths or beliefs",
                    "None - This settlement is peaceful",
                    "🔧 Custom - Specific local conflict"
                ]
            ).execute()
            
            if "Custom" in conflict_choice:
                custom_conflict = input("\n⚔️ Describe the local conflict: ").strip()
                local_conflict = f"Custom: {custom_conflict}"
            else:
                local_conflict = conflict_choice
        
        # Ask about specific NPCs
        typer.echo()
        typer.secho("👥 Do you have any specific NPCs in mind for this settlement?", fg=typer.colors.BRIGHT_GREEN)
        
        npc_choice = inquirer.select(
            message="Would you like to add specific characters?",
            choices=[
                "No, generate NPCs for me later",
                "Yes, I've got some ideas I'd like to add"
            ]
        ).execute()
        
        specific_npcs = []
        if "Yes" in npc_choice:
            typer.echo("\n👤 Great! Let's add your specific NPCs...")
            
            while True:
                npc_description = input("📝 Describe an NPC (name, role, details - or press Enter to finish): ").strip()
                if not npc_description:
                    break
                specific_npcs.append(npc_description)
                typer.echo(f"   ✅ Added: {npc_description}")
            
            if specific_npcs:
                typer.echo(f"\n🎭 Perfect! Added {len(specific_npcs)} specific NPCs to this settlement.")
        
        # Ask for settlement name after it's built
        typer.echo()
        typer.secho("🏷️ Now that we've designed this settlement, what should we call it?", fg=typer.colors.BRIGHT_BLUE)
        settlement_name = input(f"📍 Settlement name (or press Enter for auto-name): ").strip()
        if not settlement_name:
            settlement_name = f"AUTO_SETTLEMENT_{settlement_num}"
        
        return {
            'name': settlement_name,
            'type': settlement_type,
            'size': settlement_size,
            'economy': economy,
            'notable_features': notable_features,
            'local_conflict': local_conflict,
            'specific_npcs': specific_npcs
        }
    
    def get_regional_parameters(self, region_num, involvement_level):
        """Get parameters for a specific region"""
        typer.echo(f"🌍 Designing Region {region_num}...")
        
        # Region Type/Terrain (ask this first)
        region_type = inquirer.select(
            message=f"What type of region is this?",
            choices=[
                create_auto_choice("Choose perfect terrain for me!"),
                "🏔️ Mountains - Peaks, valleys, and strongholds",
                "🌲 Forest - Deep woods and hidden glades", 
                "🏞️ Plains - Rolling hills and fertile farmland",
                "🏝️ Coast - Harbors, islands, and sea trade",
                "🏜️ Desert - Vast sands and ancient ruins",
                "❄️ Tundra - Frozen lands and hardy peoples",
                "🌋 Volcanic - Fire and ash, dangerous but rich",
                "🏰 Civilized - Cities, roads, and order",
                "🌊 Islands - Archipelago of diverse cultures",
                "🌋 Swamp - Marshes, mysteries, and dangers"
            ]
        ).execute()
        
        # Political Structure (now optional)
        political_system = inquirer.select(
            message=f"How is this region governed?",
            choices=[
                create_auto_choice("Build me a government!"),
                "Monarchy - King/Queen rules with noble houses",
                "Republic - Elected leaders and councils",
                "Military State - Generals and war leaders rule",
                "Theocracy - Religious leaders hold power",
                "City-States - Independent cities allied together",
                "Tribal - Clans and chieftains lead",
                "Oligarchy - Wealthy families control everything",
                "Magocracy - Wizards and arcane powers rule",
                "Anarchy - No central authority, chaos reigns",
                "Wilderness - No formal government, just scattered communities",
                "🔧 Custom - I have something unique in mind"
            ]
        ).execute()
        
        # Regional Conflict (if DESIGNER level)
        regional_conflict = ""
        if "DESIGNER" in involvement_level:
            typer.echo(f"⚔️ What conflict or tension defines this region?")
            
            conflict_type = inquirer.select(
                message="What kind of regional conflict exists?",
                choices=[
                    create_auto_choice("Create compelling conflict!"),
                    "Civil War - Nobles/factions fight for control",
                    "Border Dispute - War with neighboring region",
                    "Resource Conflict - Fighting over mines/farmland/water",
                    "Religious Schism - Competing faiths clash",
                    "Magic Crisis - Arcane disaster or magical law debate",
                    "Rebellion - Oppressed people rise against rulers",
                    "Monster Threat - Dangerous creatures terrorize land",
                    "Natural Disaster - Ongoing environmental crisis",
                    "None - This region is peaceful for now",
                    "🔧 Custom - I have a specific conflict in mind"
                ]
            ).execute()
            
            if "Custom" in conflict_type:
                custom_conflict = input("\n⚔️ Describe the regional conflict: ").strip()
                regional_conflict = f"Custom: {custom_conflict}"
            else:
                regional_conflict = conflict_type
        
        # NOW ask for region name after it's built
        typer.echo()
        typer.secho("🏷️ Now that we've designed this region, what should we call it?", fg=typer.colors.BRIGHT_BLUE)
        region_name = input(f"📍 Region name (or press Enter for auto-name): ").strip()
        if not region_name:
            region_name = f"AUTO_REGION_{region_num}"
        
        return {
            'name': region_name,
            'type': region_type,
            'political_system': political_system,
            'regional_conflict': regional_conflict
        }

    def display_world_summary(self, result):
        """Display generated world summary"""
        typer.echo(f"\n📊 World Summary:")
        typer.echo(f"   Name: {result.world_name}")
        typer.echo(f"   Regions: {len(result.regions)}")
        typer.echo(f"   Settlements: {len(result.settlements)}")
        typer.echo(f"   NPCs: {len(result.npcs)}")
        typer.echo(f"   Conflicts: {len(result.conflicts)}")
        typer.echo(f"   Quests: {len(result.quests)}")

    def display_settlement_summary(self, settlement):
        """Display settlement summary"""
        typer.echo(f"\n📊 Settlement Summary:")
        typer.echo(f"   Name: {settlement.get('name', 'Unknown')}")
        typer.echo(f"   Population: {settlement.get('population', 0)}")
        typer.echo(f"   Buildings: {len(settlement.get('buildings', []))}")
        typer.echo(f"   NPCs: {len(settlement.get('npcs', []))}")
