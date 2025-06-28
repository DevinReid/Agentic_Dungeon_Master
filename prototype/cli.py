# cli.py
import typer
from InquirerPy import inquirer
from utils.debug_util import debug_log
from services import character_creator
from utils.dice_utility import DiceUtility

dice = DiceUtility()
app = typer.Typer()

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
