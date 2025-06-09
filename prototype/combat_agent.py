#combat_agent.py

# combat_agent.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class CombatAgent:
    def __init__(self):
        self.client = client
        # Conversation history for narration flow
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are a Dungeon Master for a D&D game. "
                    "You are neutral and do not favor the player. "
                    "You must:\n"
                    "- Narrate the outcome of the player’s actions based on the roll result and DC.\n"
                    "- If the roll result is equal to or higher than the DC, narrate success.\n"
                    "- If the roll is lower than the DC, narrate failure. "
                    "The consequences should be logical and match the severity of the situation.\n"
                    "- Critical failures (1) should have worse consequences. "
                    "Critical successes (20) should have better outcomes.\n"
                    "- Do not allow repeated attempts at the same action unless the player tries a new approach. "
                    "Narrate that the opportunity has closed after repeated failures.\n\n"
                    "Always be strict but fair, never forgiving or overly harsh. "
                    "You are the impartial Dungeon Master."
                )
            }
        ]

    def run_combat_encounter(self, player_input: str) -> str:
        """
        This method is used when the player provides an action and there is no dice roll result yet.
        It narrates the scene and sets up the situation.
        """
        self.conversation.append({"role": "user", "content": player_input})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.conversation
        )

        dm_reply = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": dm_reply})

        return dm_reply

    def narrate_roll_outcome(self, last_dm_text: str, player_input: str, roll_result: int, dc: int) -> str:
        """
        This method narrates the outcome of a dice roll.
        It should be called after the player has rolled and you have the DC.
        """
        system_prompt = (
            "You are a Dungeon Master for a D&D game. "
            "Based on the DC and the player’s roll result, decide the outcome:\n"
            "- If roll >= DC, narrate success.\n"
            "- If roll < DC, narrate failure.\n"
            "- Critical failures (1) should have worse consequences.\n"
            "- Critical successes (20) should have exceptional outcomes.\n"
            "Do not ask for another roll. Only narrate the outcome."
        )

        user_prompt = (
            f"Last DM text:\n{last_dm_text}\n\n"
            f"Player input:\n{player_input}\n"
            f"Roll result: {roll_result}\nDC: {dc}\n\n"
            "Narrate the outcome of this action."
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        narration = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": narration})
        return narration

