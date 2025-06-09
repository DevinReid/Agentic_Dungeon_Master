# cli.py
import typer
from InquirerPy import inquirer
from story_agent import StoryAgent
from db import clear_characters, create_character, get_character_sheet, update_character_stats
from combat_agent import CombatAgent, CombatManager, analyze_combat_state_ai
from dice_utility import DiceUtility
from debug_util import debug_log

dice = DiceUtility()
story = StoryAgent()
combat_agent = CombatAgent()

app = typer.Typer()

def main_menu():
    while True:
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

        if choice in ["Play", "Start New Campaign"]:
            start_new_campaign()
        elif choice == "Load Previous Campaign":
            typer.echo("Load logic placeholder")
        elif choice == "Options":
            typer.echo("Options placeholder")
        elif choice == "Quit":
            typer.echo("Goodbye!")
            raise typer.Exit()

def start_new_campaign():
    debug_log("start_new_campaign() called.")
    typer.secho("\n🛡️ Starting a New Campaign...", fg=typer.colors.GREEN)
    setup_character()
    run_intro_scene()

def setup_character():
    debug_log("setup_character() called.")
    typer.secho("\n🧙 Choose your character:", fg=typer.colors.MAGENTA)
    char_class = inquirer.select(
        message="Select your class:",
        choices=["Wizard", "Ranger", "Fighter"]
    ).execute()
    name = input("Enter your character's name: ")

    # ⚠️ Replace with LLM-based stat generation later
    level = 1
    hp = 30
    clear_characters()
    create_character(name, char_class, hp=hp)
    stats = story.generate_stats(char_class, level)
    update_character_stats(name, stats)

       # Store for later use
    global player_name, player_class
    player_name = name
    player_class = char_class

def run_intro_scene():
    debug_log("run_intro_scene() called.")
    intro = story.generate_intro(player_class, player_name)
    typer.secho("\n🪄 The Dungeon Master says:", fg=typer.colors.BRIGHT_BLUE)
    typer.echo(intro["content"])

    # Player’s first response
    action = input("\nType your action (or type 'menu' to open player choices): ")
    if action.strip().lower() == "menu":
        player_choices()
        return

    # Check if combat should start
    if analyze_combat_state_ai(intro["content"] + " " + action):
        # ⚠️ Later: dynamically create NPC stat blocks instead of hardcoding
        start_combat_loop(player_name, [{"name": "Goblin", "hp": 10, "ac": 13}])
    else:
        narration = story.story_agent(intro["content"], action)
        typer.secho("\n🪄 DM Narration:", fg=typer.colors.BRIGHT_BLUE)
        typer.echo(narration["content"])
        player_choices()

def start_combat_loop(player_name: str, npcs: list):
    debug_log("start_combat_loop() called.")
    combat_manager = CombatManager(player_name=player_name, npcs=npcs)
    combat_manager.initiative_order = ["player"] + [npc["name"] for npc in npcs]

    while not combat_manager.is_combat_over():
        current_turn = combat_manager.initiative_order[combat_manager.current_turn_index]

        if current_turn == "player":
            action = input("\nYour turn! What do you do? ")
            roll = dice.roll_dice("d20")
            success = roll >= 13  # Example AC
            #### Add analyze_combat_state_ai() here
            narration = combat_agent.narrate_combat_turn({
                "who": "player",
                "action": action,
                "roll_result": roll,
                "dc_or_ac": 13,
                "success": success,
                "damage": 8 if success else 0,
                "hp_remaining": 10
            })
            typer.echo(narration)
            #### No stats are being gewnerated or passed
        else:
            npc = combat_manager.combatants[current_turn]
            npc_action = combat_agent.decide_npc_action({
                "npc_name": npc["name"],
                "hp": npc["hp"],
                "player_ac": 15
            })
            roll = dice.roll_dice("d20")
            success = roll >= 15  # Player AC
            narration = combat_agent.narrate_combat_turn({
                "who": npc["name"],
                "action": npc_action,
                "roll_result": roll,
                "dc_or_ac": 15,
                "success": success,
                "damage": 5 if success else 0,
                "hp_remaining": 25
            })
            typer.echo(narration)

        combat_manager.next_turn()

    typer.secho("\nCombat is over. Back to the story...", fg=typer.colors.BRIGHT_BLUE)
    player_choices()

def character_sheet():
    typer.secho("\n📜 Character Sheet:", fg=typer.colors.CYAN)
    character = get_character_sheet()
    if character:
        (
            name, char_class, hp,
            strength, dexterity, constitution,
            intelligence, wisdom, charisma,
            level, experience
        ) = character
        typer.echo(f"Name: {name}\nClass: {char_class}\nLevel: {level}\nExperience: {experience}\nHP: {hp}")
        typer.echo(f"STR: {strength}  DEX: {dexterity}  CON: {constitution}")
        typer.echo(f"INT: {intelligence}  WIS: {wisdom}  CHA: {charisma}")
    else:
        typer.echo("No character found!")

def player_choices(last_story=""):
    while True:
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
        if choice == "Type an Action":
            action = input("\nWhat do you do? ")
            action_handler(last_story,action)
        elif choice == "Character Sheet":
            character_sheet()
        elif choice in ["Inventory (placeholder)", "Journal (placeholder)"]:
            typer.echo(f"{choice} shown here (placeholder)")
        elif choice == "Return to Start Menu":
            main_menu()
            break
        elif choice == "Quit Application":
            typer.secho("Goodbye!", fg=typer.colors.RED)
            raise typer.Exit()

def action_handler(last_story,action):
            combat_triggered = analyze_combat_state_ai(last_story + " " + action)

            if combat_triggered:
                # ⚠️ Needs dynamic enemy generation later
                start_combat_loop(player_name, [{"name": "Goblin", "hp": 10, "ac": 13}])
                return  # exit to combat, no further narrative
            else:
                # 2️⃣ Continue with StoryAgent
                response_json = story.story_agent(last_story, action)
                last_story = response_json["content"]  # update for next loop
                typer.secho("\n🪄 DM Narration:", fg=typer.colors.BRIGHT_BLUE)
                typer.echo(response_json["content"])

if __name__ == "__main__":
    typer.run(main_menu)
