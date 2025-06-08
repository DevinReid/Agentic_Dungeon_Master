#combat_agent.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class CombatAgent:
    def __init__(self):
        # Keep track of the conversation history
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are a Dungeon Master narrating a D&D combat encounter. "
                    "After each player response, continue the story and ask what the player does next. "
                    "Keep it concise and in the style of classic D&D combat narration."
                )
            }
        ]
    def run_combat_encounter(self, player_input: str):
        # Add the player's input to the conversation
        self.conversation.append({"role": "user", "content": player_input})

        # Send the entire conversation to the LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=self.conversation
        )

        dm_reply = response.choices[0].message.content
        # Add the DM's reply to the conversation
        self.conversation.append({"role": "assistant", "content": dm_reply})

        return dm_reply
