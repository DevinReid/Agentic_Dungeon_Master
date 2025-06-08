import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class StoryAgent:
    def __init__(self):
        self.client = client

    def generate_intro(self, character_class: str, player_name: str) -> dict:
        system_prompt = (
            "You are a Dungeon Master. "
            "Create a 5-6 sentence introduction for the player, including: "
            "who they are based on their class and name, what’s going on, why they’re here, "
            "and end with a small combat prompt for them to respond to. "
            "Return the response as JSON with keys: content, player_name, class."
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"The player's class is {character_class}. The player's name is {player_name}."}
            ],
            response_format="json"  # Direct JSON return
        )

        json_string = response.choices[0].message.content
        return json.loads(json_string)
