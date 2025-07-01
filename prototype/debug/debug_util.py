# debug_util.py
import typer



DEBUG_MODE = False  # Toggle this globally!

def debug_log(message: str):
    if DEBUG_MODE:
        from typer import secho
        secho(f"DEBUG: {message}", fg="red")


class DebugUtils:
    def __init__(self, game_session=None, combat_manager=None):
        self.game_session = game_session
        self.combat_manager = combat_manager

    def activate_god_mode(self):
        """Activate god mode - max HP and AC"""
        if self.game_session:
            typer.secho("🛡️ DEBUG: God mode activated!", fg=typer.colors.BRIGHT_YELLOW)
            self.game_session.character["hp"] = 999
            self.game_session.character["ac"] = 25
            if self.combat_manager:
                self.combat_manager.combatants["player"]["hp"] = 999
                self.combat_manager.combatants["player"]["ac"] = 25
        input("\n📖 Press Enter to continue...")

    def full_heal(self):
        """Full heal the character"""
        if self.game_session:
            typer.secho("💚 DEBUG: Full heal!", fg=typer.colors.BRIGHT_GREEN)
            max_hp = self.game_session.character.get("max_hp", 100)
            self.game_session.character["hp"] = max_hp
            if self.combat_manager:
                self.combat_manager.combatants["player"]["hp"] = max_hp
        input("\n📖 Press Enter to continue...")

    def kill_all_enemies(self):
        """Kill all enemies in combat"""
        if self.combat_manager:
            typer.secho("🎯 DEBUG: Killing all enemies...", fg=typer.colors.BRIGHT_RED)
            for name, npc in self.combat_manager.combatants.items():
                if name != "player":
                    npc["hp"] = 0
            typer.echo("All enemies defeated!")
        else:
            typer.echo("❌ Kill command only works in combat!")
        input("\n📖 Press Enter to continue...")

    def add_resources(self):
        """Add gold/items (placeholder)"""
        typer.echo("🚧 Add resources feature - coming soon!")
        input("\n📖 Press Enter to continue...")

    def level_up_character(self):
        """Level up character (placeholder)"""
        typer.echo("🚧 Level up feature - coming soon!")
        input("\n📖 Press Enter to continue...")