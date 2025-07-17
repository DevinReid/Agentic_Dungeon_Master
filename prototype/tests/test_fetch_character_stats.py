import json
from openai import OpenAI
from dotenv import load_dotenv
import pytest

load_dotenv()
client = OpenAI()

def fetch_character_stats(universe_characters, target_character_description, target_stat_name) -> str:
        system_prompt = (
            "You are to receive a list of characters. "
            "You will be given a description of a single characters, "
            "Do your best to pick the characters that fits the description back "
            "Do not respond in a question, you must pick a character from the list exclusively"
            "Once you find the character, return the information field associated with the target statistic"
            "You should only respond with a single number"
        )
        user_prompt = f"""
            The list characters are:\n{universe_characters}, 
            The character you're looking for is like {target_character_description}.
            The target statistic is {target_stat_name}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return int(response.choices[0].message.content)

# Assuming 'data.json' is the name of your JSON file
# and it's located in the same directory as your Python script.
with open('characters.json', 'r') as file: 
    universe_characters = json.load(file)

def test_fetch_character_stats():
    assert 1 == 1

def test_basic_character():
    test_description = "A friendly golem guardian"
    target_statistic = "strength"
    solution_strength_stat = fetch_character_stats(universe_characters, test_description, target_statistic)
    print(solution_strength_stat)
    assert solution_strength_stat == 6

def test_less_descriptive_character():
    test_description = "A golem"
    target_statistic = "strength"
    solution_strength_stat = fetch_character_stats(universe_characters, test_description, target_statistic)
    print(solution_strength_stat)
    assert solution_strength_stat == 6 