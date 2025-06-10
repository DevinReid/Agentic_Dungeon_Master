import json
import random
import cli
from debug_util import debug_log
from openai import OpenAI
from dotenv import load_dotenv
from combat_agent import CombatAgent
from dice_utility import DiceUtility
import game_session 

load_dotenv()
client = OpenAI()
session = game_session.GameSession()
dice = DiceUtility()
combat_agent = CombatAgent()

def analyze_combat_state_ai(last_dm_text: str, player_response) -> bool:
    debug_log("analyze_combat_state_ai() called.")
    system_prompt = (
        "You are a Dungeon Master assistant. Based on the following narration, "
        "determine if combat has started or if combat is ongoing. "
        "Respond with JSON: {\"combat\": true} or {\"combat\": false}."
    )
    user_prompt = (
        f"Dungeon Master's Narration text:\n{last_dm_text}\n\n"
        f"Player's Response:\n{player_response}\n\nIs combat happening?"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    combat_state = json.loads(response.choices[0].message.content)
    return combat_state["combat"]

class CombatManager:
    def __init__(self, player_name: str, npcs: list):
        debug_log("CombatManager.__init__() called.")
        self.combatants = {"player": {"name": player_name, "hp": session.character.hp, "ac": 15}}
        for npc in npcs:
            self.combatants[npc["name"]] = npc

        self.initiative_order = []
        self.current_turn_index = 0
        self.round = 1

    def initialize_initiative(self):
        combatants_initiative = []
        for name, stats in self.combatants.items():
            modifier = 0
            initiative = random.randint(1, 20) + modifier
            combatants_initiative.append({"name": name, "initiative": initiative})

        combatants_initiative.sort(key=lambda x: x["initiative"], reverse=True)
        self.initiative_order = [c["name"] for c in combatants_initiative]

        print("\nInitiative Order:")
        for c in combatants_initiative:
            print(f"  {c['name']}: {c['initiative']}")

    def next_turn(self):
        debug_log("CombatManager.next_turn() called.")
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        if self.current_turn_index == 0:
            self.round += 1
            print(f"\n--- Round {self.round} ---")

    def current_combatant(self):
        return self.initiative_order[self.current_turn_index]

    def is_combat_over(self):
        debug_log("CombatManager.is_combat_over() called.")
        player_hp = self.combatants["player"]["hp"]
        npcs_alive = [c for n, c in self.combatants.items() if n != "player" and c["hp"] > 0]
        return player_hp <= 0 or not npcs_alive

    def print_combatants_status(self):
        print("\n-- Combatant Status --")
        for name, stats in self.combatants.items():
            print(f"  {name}: {stats['hp']} HP")

    def run_combat(self):
        print("\nCombat begins!")
        while not self.is_combat_over():
            who = self.current_combatant()
            print(f"\n-- {who.capitalize()}'s Turn --")

            if who == "player":
                handle_player_turn(self)
            else:
                handle_npc_turn(self, who)

            self.print_combatants_status()
            self.next_turn()
        print("\nCombat has ended.")
        session.in_combat=False

def handle_player_turn(combat_manager):
    action = input("\nYour turn! What do you do? (e.g., Attack) ")
    target = next((c for n, c in combat_manager.combatants.items() if n != "player" and c["hp"] > 0), None)
    if not target:
        return  # No NPCs left

    roll = dice.roll_dice("d20")
    success = roll >= target["ac"]
    damage = random.randint(1, 8) if success else 0
    target["hp"] -= damage

    
    cli.ui_show_roll("player", roll)
    cli.ui_show_damage("player", damage, success)

    turn_info = {
        "who": "player",
        "action": action,
        "roll_result": roll,
        "dc_or_ac": target["ac"],
        "success": success,
        "damage": damage,
        "hp_remaining": target["hp"]
    }
    narration = combat_agent.narrate_combat_turn(turn_info)
    print(narration)

def handle_npc_turn(combat_manager, npc_name):
    npc = combat_manager.combatants[npc_name]
    npc_action = combat_agent.decide_npc_action({
        "npc_name": npc["name"],
        "hp": npc["hp"],
        "player_ac": combat_manager.combatants["player"]["ac"]
    })

    roll = dice.roll_dice("d20")
    success = roll >= combat_manager.combatants["player"]["ac"]
    damage = random.randint(1, 6) if success else 0
    combat_manager.combatants["player"]["hp"] -= damage

    cli.ui_show_roll(npc_name, roll)
    cli.ui_show_damage(npc_name, damage, success)

    turn_info = {
        "who": npc["name"],
        "action": npc_action,
        "roll_result": roll,
        "dc_or_ac": combat_manager.combatants["player"]["ac"],
        "success": success,
        "damage": damage,
        "hp_remaining": combat_manager.combatants["player"]["hp"]
    }
    narration = combat_agent.narrate_combat_turn(turn_info)
    print(narration)

if __name__ == "__main__":
    npcs = [{"name": "Goblin", "hp": 10, "ac": 13}]
    combat_manager = CombatManager(player_name="Hero", npcs=npcs)
    combat_manager.initialize_initiative()
    combat_manager.run_combat()
