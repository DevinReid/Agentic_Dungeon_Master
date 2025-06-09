# combat_system.py

import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


# 🟩 Combat State Analyzer
def analyze_combat_state_ai(narration_text: str) -> bool:
    system_prompt = (
        "You are a Dungeon Master assistant. Based on the following narration, "
        "determine if combat has started or if combat is ongoing. "
        "Respond with JSON: {\"combat\": true} or {\"combat\": false}."
    )

    user_prompt = f"Narration text:\n{narration_text}\n\nIs combat happening?"

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


# 🟩 Combat Manager
class CombatManager:
    def __init__(self, player_name: str, npcs: list):
        self.initiative_order = []
        self.current_turn_index = 0
        self.round = 1
        self.combatants = {"player": {"name": player_name, "hp": 30, "ac": 15}}
        for npc in npcs:
            self.combatants[npc["name"]] = npc

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        if self.current_turn_index == 0:
            self.round += 1

    def is_combat_over(self):
        player_hp = self.combatants["player"]["hp"]
        npcs_alive = [c for n, c in self.combatants.items() if n != "player" and c["hp"] > 0]
        return player_hp <= 0 or not npcs_alive


# 🟩 Combat Agent
class CombatAgent:
    def __init__(self):
        self.client = client

    def narrate_combat_turn(self, turn_info: dict) -> str:
        """
        Narrate the outcome of a single combat turn.
        """
        system_prompt = (
            "You are a Dungeon Master for a D&D combat encounter. "
            "You receive the result of the player's or NPC's turn, including whether they hit or missed, "
            "and you must narrate the outcome of this action in a neutral, immersive way. "
            "Always keep it short, like 2-3 sentences, and never fudge the outcome."
        )

        user_prompt = (
            f"Turn Info:\n{turn_info}\n\n"
            "Narrate the outcome of this combat turn."
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.choices[0].message.content

    def decide_npc_action(self, npc_info: dict) -> str:
        """
        Decide the NPC's next combat action.
        """
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


