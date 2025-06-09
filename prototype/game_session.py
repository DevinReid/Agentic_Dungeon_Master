# game_session.py
import cli
from story_agent import StoryAgent
from db import clear_characters, create_character, update_character_stats
from combat_agent import CombatAgent, CombatManager, analyze_combat_state_ai
from dice_utility import DiceUtility
from debug_util import debug_log

class GameSession:
    def __init__(self):
        self.dice = DiceUtility()
        self.story = StoryAgent()
        self.combat_agent = CombatAgent()
        self.session_context = ""
        self.last_dm_text = ""
        self.player_name = ""
        self.player_class = ""

    def setup_character(self, name, char_class):
        debug_log("setup_character() called.")
        self.player_name = name
        self.player_class = char_class
        level = 1
        hp = 30
        clear_characters()
        create_character(name, char_class, hp=hp)
        stats = self.story.generate_stats(char_class, level)
        update_character_stats(name, stats)

    def run_intro_scene(self):
        debug_log("run_intro_scene() called.")
        intro = self.story.generate_intro(self.player_class, self.player_name)
        self.session_context += f"\nDM: {intro['content']}"
        self.last_dm_text = intro["content"]
        return intro["content"]

    def action_handler(self, action):
        combat_triggered = analyze_combat_state_ai(self.last_dm_text, action)
        if combat_triggered:
            return "combat"

        roll_info = self.dice.analyze_for_roll(self.last_dm_text, action)
        if roll_info.get('roll_needed'):
            result = self.dice.roll_dice(roll_info['dice_type'])
            cli.ui_handle_dice_roll(roll_info, result)
            success = self.dice.determine_success(roll_info, result)
            cli.ui_declare_dice_result(success)
        else:
            success = "No result required"

        response_json = self.story.story_agent(
            self.session_context, action,
            roll_info.get('roll_needed'),
            roll_info.get('roll_type'),
            roll_info.get('dc'),
            success
        )
        new_dm_text = response_json["content"]
        self.session_context += f"\nPlayer: {action}\nDM: {new_dm_text}"
        self.last_dm_text = new_dm_text
        return new_dm_text


    def start_combat_loop(self):
        combat_manager = CombatManager(player_name=self.player_name, npcs=[{"name": "Goblin", "hp": 10, "ac": 13}])
        combat_manager.initiative_order = ["player"] + [npc["name"] for npc in combat_manager.npcs]

        while not combat_manager.is_combat_over():
            current_turn = combat_manager.initiative_order[combat_manager.current_turn_index]

            if current_turn == "player":
                # Leave CLI to handle user input for player action
                pass
            else:
                npc = combat_manager.combatants[current_turn]
                npc_action = self.combat_agent.decide_npc_action({
                    "npc_name": npc["name"],
                    "hp": npc["hp"],
                    "player_ac": 15
                })
                roll = self.dice.roll_dice("d20")
                success = roll >= 15
                narration = self.combat_agent.narrate_combat_turn({
                    "who": npc["name"],
                    "action": npc_action,
                    "roll_result": roll,
                    "dc_or_ac": 15,
                    "success": success,
                    "damage": 5 if success else 0,
                    "hp_remaining": 25
                })
                print(narration)
            combat_manager.next_turn()

        return "Combat ended"
