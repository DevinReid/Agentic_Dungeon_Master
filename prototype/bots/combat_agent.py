import json
from openai import OpenAI
from dotenv import load_dotenv
from utils.debug_util import debug_log

load_dotenv()
client = OpenAI()

class CombatAgent:
    def __init__(self):
        debug_log("CombatAgent.__init__() called.")
        self.client = client

    def narrate_combat_turn(self, turn_info: dict) -> str:
        debug_log("CombatAgent.narrate_combat_turn() called.")
        system_prompt = (
            "You are a Dungeon Master for a D&D combat encounter. "
            "You receive the result of the player's or NPC's turn, including whether they hit or missed, "
            "and you must narrate the outcome of this action in a neutral, immersive way. "
            "Always keep it short, like 2-3 sentences, and never fudge the outcome."
        )
        user_prompt = f"Turn Info:\n{turn_info}\n\nNarrate the outcome of this combat turn."

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    def decide_npc_action(self, npc_info: dict) -> str:
        debug_log("CombatAgent.decide_npc_next_action() called.")
        system_prompt = (
            "You are the DM. Given this NPC's status and environment, decide their next combat action. "
            "Reply in a single sentence with the NPC's chosen action, no extra commentary."
        )
        user_prompt = f"NPC Info:\n{npc_info}\n\nWhat is the NPC's action?"

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
