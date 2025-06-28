import os
from openai import OpenAI
from dotenv import load_dotenv
import uuid
import json

load_dotenv()
client = OpenAI()

class NpcCreatorAgent:
    def __init__(self):
        self.client = client

    def generate_stats(self, character_class: str, level: int = 1) -> dict:
        system_prompt = (
            "You are a D&D character creator assistant. "
            "Given a character's class and level, generate a basic stat block as JSON. "
            "Return exactly this JSON structure:\n"
            "{\n"
            "  \"strength\": [number 8-18],\n"
            "  \"dexterity\": [number 8-18],\n"
            "  \"constitution\": [number 8-18],\n"
            "  \"intelligence\": [number 8-18],\n"
            "  \"wisdom\": [number 8-18],\n"
            "  \"charisma\": [number 8-18],\n"
            "  \"level\": [number],\n"
            "  \"experience\": [number, 0 for level 1],\n"
            "  \"hp\": [number],\n"
            "  \"ac\": [number]\n"
            "}\n"
            "Use typical D&D stat ranges and appropriate HP/AC for the class."
        )

        user_prompt = f"Class: {character_class}\nLevel: {level}"

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
             response_format={"type": "json_object"} 
        )

        json_string = response.choices[0].message.content
        return json.loads(json_string)

    def generate_character_sheet(self, description: str, player_character_names: list[str], level: int = 1):
        system_prompt = """
            You are a Dungeon Master Assistant.
            You will be given a narration from the dungeon master. 
            Your job is to parse the narration for NPCs or Monsters.
            The parsed output should be a JSON of the characters with an array of objects that contains their names from the context and a class as a string.
            If you can't find a name, make it the same as the class.
            If there is a plural noun for an character, make a new entry in the array so that each entry is singular.
            Names should be unique, you can increment names like Person 1 and Person 2.
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

        found_characters = json.loads(response.choices[0].message.content)["characters"]
        completed_characters = []
        for character in found_characters:
            descriptions = self.generate_stats(character_class=character['class'])
            updated_character = {
                "id": str(uuid.uuid4()),
                "name":character["name"],
                "class":character["class"],
                "hp": descriptions["hp"],
                "strength": descriptions["strength"],
                "dexterity": descriptions["dexterity"],
                "constitution": descriptions["constitution"],
                "intelligence": descriptions["intelligence"],
                "wisdom": descriptions["wisdom"],
                "charisma": descriptions["charisma"],
                "level": descriptions["level"],
                "experience": descriptions["experience"],
                "ac": descriptions["ac"],
            }
            completed_characters.append(updated_character)
        return completed_characters
