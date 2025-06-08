import typer
from combat_agent import CombatAgent

app = typer.Typer()
agent = CombatAgent()

@app.command()
def hello_combat():
    """
    Run a simple combat encounter.
    """
    narration = agent.run_combat_encounter()
    typer.secho("\n🎲 Combat Encounter:", fg=typer.colors.BRIGHT_GREEN)
    typer.echo(narration)

if __name__ == "__main__":
    typer.run(hello_combat)
