# game_session.py
import cli
from prototype.bots.story_agent import StoryAgent
from db import clear_characters, create_character, update_character_stats, get_character_sheet
from combat_agent import CombatAgent
from combat_system import CombatManager, analyze_combat_state_ai
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
        self.in_combat = False
        self.character={}

        
        self.load_character_stats()

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


    def start_combat(self, npc_names):
        npcs = [{"name": name, "hp": 10, "ac": 13} for name in npc_names]
        self.combat_manager = CombatManager(player_name=self.player_name, npcs=npcs, player_hp = self.character["hp"], player_ac= self.character["ac"])
        self.combat_manager.initialize_initiative()
        self.combat_manager.current_turn_index = 0
        self.combat_manager.round = 1
        self.combat_manager.run_combat()
        ## If Combat has already started we want to avoid rerolling initiative


    def load_character_stats(self):
        character = get_character_sheet()
        if character:
            (
                name, char_class, hp,
                strength, dexterity, constitution,
                intelligence, wisdom, charisma,
                level, experience, ac
            ) = character

            self.character = {
                "name": name,
                "class": char_class,
                "hp": hp,
                "strength": strength,
                "dexterity": dexterity,
                "constitution": constitution,
                "intelligence": intelligence,
                "wisdom": wisdom,
                "charisma": charisma,
                "level": level,
                "experience": experience,
                "ac": ac
            }



