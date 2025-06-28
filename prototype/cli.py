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
