#dice_utility.py

import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv
from .debug_util import debug_log
load_dotenv()
client = OpenAI()

class DiceUtility:
    def __init__(self):
        self.client = client

    def analyze_for_roll(self, last_dm_text: str, player_input: str = "") -> dict:

        debug_log("analyze_for_roll() called.")
        system_prompt = (
              "You are a Dungeon Master rules assistant. "
                "Given the last DM narration and the player's input, determine:\n"
                "- roll_needed: true or false\n"
                "- dice_type: e.g., d20, d6\n"
                "- roll_type: the type of roll needed, e.g., 'Persuasion', 'Attack', 'Stealth', 'Perception', etc.\n"
                "- roll_reason: a short explanation\n"
                "- dc: a numeric Difficulty Class (DC) based on the situation\n\n"
                
                "Respond in JSON only."
            )
                

        user_prompt = (
            f"Last DM text:\n{last_dm_text}\n\n"
            f"Player input:\n{player_input}\n\n"
            "Decide if a dice roll is needed and explain the type and reason."
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    def roll_dice(self, dice_type) -> int:
        
        debug_log("roll_dice() called.")
        if dice_type == "d20":
            return random.randint(1, 20)
        elif dice_type == "d6":
            return random.randint(1, 6)
        # Add other dice as needed
        return 
          # Default


    def determine_success(self, roll_info, dice_result):
        dc = roll_info['dc']
        if dice_result == 1:
            return "Critical Failure!"
        elif dice_result == 20:
            return "Critical Success!"
        elif dice_result < dc:
            return "Failure"
        else:
            return "Success"