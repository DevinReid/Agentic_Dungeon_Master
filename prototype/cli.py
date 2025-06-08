#cli.py
import typer
from InquirerPy import inquirer
from combat_agent import CombatAgent
from story_agent import StoryAgent


app = typer.Typer()
combat = CombatAgent()
story = StoryAgent()

''' START MENU '''

def start_new_campaign():
    typer.secho("\n🛡️ Starting a New Campaign...", fg=typer.colors.GREEN)
    typer.echo("New campaign setup logic here.")
    player_choices()

def load_previous_campaign():
    typer.secho("\n📜 Load Previous Campaign:", fg=typer.colors.CYAN)
    typer.echo("Load game logic here.")
    player_choices()

def options_menu():
    typer.secho("\n⚙️ Game Options:", fg=typer.colors.YELLOW)
    typer.echo("No options configured yet!")

def main_menu():
    while True:
        choice = inquirer.select(
            message="Welcome to Agentic Dungeon Master! Choose an option:",
            choices=[
                "Play",  # 🚀 NEW button at the top
                "Start New Campaign",
                "Load Previous Campaign",
                "Options",
                "Quit"
            ]
        ).execute()

        if choice == "Play":
            typer.secho("\n🎮 Launching into the game!", fg=typer.colors.GREEN)
            character_select() # Same logic as Start New Campaign
        elif choice == "Start New Campaign":
            start_new_campaign()
        elif choice == "Load Previous Campaign":
            load_previous_campaign()
        elif choice == "Options":
            options_menu()
        elif choice == "Quit":
            typer.secho("Goodbye!", fg=typer.colors.RED)
            raise typer.Exit()
        
''' CAMPAIGN SETUP '''
def character_select():
    typer.secho("\n🧙 Choose your character:", fg=typer.colors.MAGENTA)
    choice = inquirer.select(
        message="Select your class:",
        choices=["Wizard", "Ranger", "Fighter"]
    ).execute()

    typer.secho(f"\nYou have chosen: {choice}!", fg=typer.colors.GREEN)
    
    # Use StoryAgent to generate intro
    intro_narration = story.generate_intro(choice)
    
    typer.secho("\n🪄 The Dungeon Master says:", fg=typer.colors.BRIGHT_BLUE)
    typer.echo(intro_narration)
    typer.echo()  # blank line for spacing

    # Feed intro to combat agent
    combat.conversation.append({"role": "assistant", "content": intro_narration})

    # Start combat loop
    type_action()

''' PLAYER CHOICES MENU '''

def type_action():
    typer.secho("\n🎲 Combat Encounter Begins!", fg=typer.colors.BRIGHT_GREEN)
    player_input = input("Type your action (or type 'menu' to open player choices): ")

    while True:
        if player_input.strip().lower() == "menu":
            typer.secho("\n📜 Returning to Player Choices Menu!", fg=typer.colors.GREEN)
            player_choices()

        narration = combat.run_combat_encounter(player_input)
        typer.secho("\n🪄 DM Narration:", fg=typer.colors.BRIGHT_BLUE)
        typer.echo(narration)
        player_input = input("\nType your next action (or type 'menu' to open player choices): ")

def character_sheet():
    typer.secho("\n📜 Character Sheet:", fg=typer.colors.CYAN)
    typer.echo("Name: Devin the Brave\nHP: 25/30\nStrength: 14")
    typer.echo()


def inventory():
    typer.secho("\n🎒 Inventory:", fg=typer.colors.YELLOW)
    typer.echo("Backpack: 1x Health Potion, 10x Gold Coins")
    typer.echo()


def journal():
    typer.secho("\n📖 Journal:", fg=typer.colors.MAGENTA)
    typer.echo("Journal:\n- Met goblin in dark cave.\n- Found mysterious shard.")
    typer.echo()


def player_choices():
    while True:
        choice = inquirer.select(
            message="Choose an option:",
            choices=[
                "Type an Action",
                "Character Sheet",
                "Inventory",
                "Journal",
                "In-Game Menu"
            ]
        ).execute()

        if choice == "Type an Action":
            type_action()
        elif choice == "Character Sheet":
            character_sheet()
        elif choice == "Inventory":
            inventory()
        elif choice == "Journal":
            journal()
        elif choice == "In-Game Menu":
            game_menu()

''' IN-GAME MENU '''

def game_menu():
    while True:
        # Use Typer's secho to print the prompt in pink (magenta)
        typer.secho("\nIn-Game Menu:", fg=typer.colors.MAGENTA, bold=True)

        choice = inquirer.select(
            message="",
            choices=[
                "Return to Game",
                "View Artifacts",
                "Talk to DM",
                "Options",
                "Save game",
                "Load Game",
                "Return to Start Menu",
                "Return to Campaign Menu",
                "Quit Application"
            ]
        ).execute()

        if choice == "Return to Game":
            typer.secho("\n🎮 Returning to the game!", fg=typer.colors.GREEN)
            break
        elif choice == "View Artifacts":
            typer.echo("\n🔮 Viewing your artifacts... (placeholder)")
        elif choice == "Talk to DM":
            typer.echo("\n🗣️ Talking to the Dungeon Master... (placeholder)")
        elif choice == "Options":
            typer.echo("\n⚙️ Adjusting options... (placeholder)")
        elif choice == "Save game":
            typer.echo("\n💾 Saving your game... (placeholder)")
        elif choice == "Load Game":
            typer.echo("\n📜 Loading a game... (placeholder)")
        elif choice == "Return to Start Menu":
            typer.secho("\n🏠 Returning to Start Menu!", fg=typer.colors.GREEN)
            main_menu()
            break
        elif choice == "Return to Campaign Menu":
            typer.secho("\n🛡️ Returning to Campaign Menu!", fg=typer.colors.BLUE)
            player_choices()
            break
        elif choice == "Quit Application":
            typer.secho("Goodbye!", fg=typer.colors.RED)
            raise typer.Exit()


''' ENTRY POINT '''

if __name__ == "__main__":
    typer.run(main_menu)

