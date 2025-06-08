import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class StoryAgent:
    def __init__(self):
        self.client = client

    def generate_intro(self, character_class: str) -> str:
        """
        Generates a 5-6 sentence intro for the chosen character class.
        Covers: who you are, what’s going on, why you’re here, and ends with a combat prompt.
        """
        system_prompt = (
            "You are a Dungeon Master. "
            "Create a 5-6 sentence introduction for the player, including: "
            "who they are based on their class, what’s going on, why they’re here, "
            "and end with a small combat prompt for them to respond to."
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"The player's class is: {character_class}."}
            ]
        )

        intro_narration = response.choices[0].message.content
        return intro_narration
