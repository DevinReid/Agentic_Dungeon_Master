# master.py
import cli
from game_session import GameSession

def start_game():
    while True:
        choice = cli.ui_main_menu()
        if choice in ["Play", "Start New Campaign"]:
            start_new_campaign()
        elif choice == "Load Previous Campaign":
            print("Load logic placeholder")
        elif choice == "Options":
            print("Options placeholder")
        elif choice == "Quit":
            cli.ui_quit()
            break

def start_new_campaign():
    cli.ui_start_new_campaign()
    name, char_class = cli.ui_setup_character()
    session = GameSession()
    session.setup_character(name, char_class)
    intro_text = session.run_intro_scene()
    cli.ui_display_dm_narration(intro_text)
    player_choices(session)

def player_choices(session):
    while True:
        choice = cli.ui_player_choice()
        if choice == "Type an Action":
            action = cli.ui_get_action()
            if action.strip().lower() == "menu":
                return
            result = session.action_handler(action)
            if result == "combat":
                start_combat(session)
            else:
                cli.ui_display_dm_narration(result)
        elif choice == "Character Sheet":
            cli.ui_character_sheet()
        elif choice in ["Inventory (placeholder)", "Journal (placeholder)"]:
            cli.typer.echo(f"{choice} shown here (placeholder)")
        elif choice == "Return to Start Menu":
            return
        elif choice == "Quit Application":
            cli.ui_quit()

def start_combat(session):
    session.start_combat_loop()
    cli.ui_combat_over()
    player_choices(session)

if __name__ == "__main__":
    start_game()
