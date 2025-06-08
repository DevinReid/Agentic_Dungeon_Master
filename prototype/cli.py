#cli.py

import typer
from combat_agent import CombatAgent

app = typer.Typer()
agent = CombatAgent()

def interactive_combat():
    """
    Run an interactive combat encounter in the terminal.
    """
    typer.secho("\n🎲 Combat Encounter Begins!", fg=typer.colors.BRIGHT_GREEN)
    
    # First prompt to start the scene
    player_input = "Describe a goblin attacking the player with a short dramatic narration."

    while True:
        # Get the DM's narration
        dm_narration = agent.run_combat_encounter(player_input)
        typer.secho("\n🪄 DM Narration:", fg=typer.colors.BRIGHT_BLUE)
        typer.echo(dm_narration)

        # Prompt the player for their response
        player_input = input("\n💬 Your action (or type 'quit' to end): ")

        if player_input.strip().lower() == "quit":
            typer.secho("\n🎲 Combat encounter ends. Goodbye!", fg=typer.colors.RED)
            break

if __name__ == "__main__":
    typer.run(interactive_combat)
