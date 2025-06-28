import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from utils.debug_util import debug_log

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
            response_format={"type": "json_object"}  # Direct JSON return
        )

        json_string = response.choices[0].message.content
        return json.loads(json_string)

    def generate_stats(self, character_class: str, level: int) -> dict:
        system_prompt = (
            "You are a D&D character creator assistant. "
            "Given a character's class and level, generate a basic stat block as JSON. "
            "Return fields: strength, dexterity, constitution, intelligence, wisdom, charisma, level, experience, hp, ac. "
            "Use typical stat ranges (8-18) and assign experience as 0 for level 1."
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

    def story_agent(self, last_story: str, player_input: str, roll_needed: bool, roll_type: str, dc: int, success: str) -> dict:
        debug_log("Story_Agent() called.")
        """
        Given the last story narration and the player's response,
        continue narrating the scene (social or exploration, not combat).
        Returns JSON with fields: content, player_name (optional), location (optional), etc.
        """
        system_prompt = (
            "You are the Dungeon Master for a D&D game, responsible for all narrative scenes outside of structured combat turns. "
            "You create immersive descriptions, dialogues, and events in the world, including managing story beats, NPC interactions, and exploration. "
            "You must also be able to escalate tension and initiate combat narratively if the player's actions or the situation demand it—such as describing NPC aggression, traps, or ambushes that would trigger combat. "
            "Combat mechanics (like rolling dice, calculating damage, or hit points) are handled by Python code and the CombatAgent; you do not do any of that yourself. "
            "Combat will never trigger if you don’t set it up narratively. "
            "Another agent (the Combat State Analyzer) will analyze your narration for signs of combat initiation or hostility. "
            "If you want combat to begin, you must describe the aggression or attack clearly—otherwise, it will remain a social or exploration scene. "
            "You remember previous narrations and story details to ensure consistency and continuity. "
            "You always continue the story from the last point and the player's input, building upon what has already happened. "
            "Return your narration as JSON with at least the 'content' field."
        )


        user_prompt = (
            f"Last narration:\n{last_story}\n\n"
            f"Player input:\n{player_input}\n\n"
            f"Did the character need to roll? \n{roll_needed}\n\n"
            f"If the character needed to roll, what kind of roll was required? \n {roll_type}\n\n"
            f"What was the Difficulty Class(DC) of the attempt the character is trying to beat? \n {dc}"
            f"What was the outcome of the roll? \n {success}\n\n"
            "Continue the scene and return JSON: {\"content\": \"...\"}"
        )

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