import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from debug_util import debug_log
from story_agent import StoryAgent

load_dotenv()
client = OpenAI()

fields = [
    "id",
    "name",
    "class",
    "hp",
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
    "level",
    "experience",
    "ac"
]

class NpcCreatorAgent:
    def __init__(self):
        self.client = client
        self.story_agent = StoryAgent

    def generate_character_sheet(self, description: str, player_character_names: list[str]):
        system_prompt = """
            You are a Dungeon Master Assistant.
            You will be given a narration from the dungeon master. 
            Your job is to parse the narration for NPCs or Monsters.
            The parsed output should be a JSON of characters with an array of objects that contains a name, a class as a string, and a count.
            If there is a plural noun for an NPC, consider increasing the count or making multiple unique named NPCs or Monsters.
            Do not include any of the characters names, which will be given to you.
        """

        user_prompt = f"""
            This is the story description containing the characters: {description}.
            This is a list of known character names to exclude: {", ".join(player_character_names)}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
             response_format={"type": "json_object"} 
        )

        print(response.choices[0].message.content)

        return response.choices[0].message.content

