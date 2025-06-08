# from openai import OpenAI
# import json

# client = OpenAI()

# class CombatAgent:
#     def handle_combat(self, scene_description: str, player_name: str):
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             response_format="json",  # 👈 structured response!
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a Dungeon Master narrating a combat sequence. "
#                         "Return only JSON like this: "
#                         '{"narration": "...", "damage": 8}'
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": scene_description
#                 }
#             ]
#         )

#         json_string = response.choices[0].message.content
#         combat_data = json.loads(json_string)

#         narration = combat_data["narration"]
#         damage = combat_data["damage"]

#         print("\n🎲 Combat Narration:\n", narration)
#         print("Damage:", damage)
#         # Your logic to update health would go here

# # Example usage
# agent = CombatAgent()
# agent.handle_combat("The goblin swings at the player.", player_name="Devin")


import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class CombatAgent:
    def run_combat_encounter(self):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Dungeon Master. Create a very short combat encounter "
                        "narration that ends after describing the attack."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Describe a goblin attacking the player with a short dramatic narration."
                    )
                }
            ]
        )
        narration = response.choices[0].message.content
        return narration
