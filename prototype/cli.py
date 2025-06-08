#cli.py
import typer
from InquirerPy import inquirer
from combat_agent import CombatAgent

app = typer.Typer()
agent = CombatAgent()

def type_action():
    typer.secho("\n🎲 Combat Encounter Begins!", fg=typer.colors.BRIGHT_GREEN)

    # Initial prompt
    player_input = input("Type your action (or type 'quit' to end): ")

    while True:
        if player_input.strip().lower() == "quit":
            typer.secho("\n🎲 Combat encounter ends. Goodbye!", fg=typer.colors.RED)
            break

        # Send player's input to the DM
        narration = agent.run_combat_encounter(player_input)
        typer.secho("\n🪄 DM Narration:", fg=typer.colors.BRIGHT_BLUE)
        typer.echo(narration)

        # Prompt the player again
        player_input = input("\nType your next action (or type 'quit' to end): ")

def character_sheet():
    typer.secho("\n📜 Character Sheet:", fg=typer.colors.CYAN)
    typer.echo("Name: Devin the Brave\nHP: 25/30\nStrength: 14")

def inventory():
    typer.secho("\n🎒 Inventory:", fg=typer.colors.YELLOW)
    typer.echo("Backpack: 1x Health Potion, 10x Gold Coins")

def journal():
    typer.secho("\n📖 Journal:", fg=typer.colors.MAGENTA)
    typer.echo("Journal:\n- Met goblin in dark cave.\n- Found mysterious shard.")

def main_menu():
    choices = [
        "Type an Action",
        "Character Sheet",
        "Inventory",
        "Journal",
        "Quit"
    ]
    choice = inquirer.select(
        message="Choose an option:",
        choices=choices
    ).execute()

    if choice == "Type an Action":
        type_action()
    elif choice == "Character Sheet":
        character_sheet()
    elif choice == "Inventory":
        inventory()
    elif choice == "Journal":
        journal()
    elif choice == "Quit":
        typer.secho("Goodbye!", fg=typer.colors.RED)
        raise typer.Exit()

if __name__ == "__main__":
    typer.run(main_menu)
