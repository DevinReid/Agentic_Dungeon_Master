import cli
from services.game_session import GameSession
from db.db import (create_character, update_character_stats, get_or_create_user)

class CharacterCreator:
    def __init__(self, campaign_id, username):
        self.campaign_id = campaign_id
        self.username = username
        self.user_id = get_or_create_user(username)

    def create_new_character(self):
        """Create a new character for a campaign"""
        
        # Get character details from CLI
        name = cli.ui_get_char_name()
        char_class = cli.ui_get_char_class()
        
        # # Clear any existing characters in this campaign for this user (for testing)
        # existing_char = get_character_in_campaign(self.campaign_id, self.user_id)
        # if existing_char:
        #     clear_characters_in_campaign(self.campaign_id)
  
        # Generate stats using story agent (you'll need to import StoryAgent)
        from bots.story_agent import StoryAgent  # or wherever StoryAgent is
        story_agent = StoryAgent()
        stats = story_agent.generate_stats(char_class, 1)
        stats["ac"] = stats["ac"] + 2
        stats["hp"] = stats["hp"] + 50
        stats["max_hp"] = stats["hp"]

        # Create character with real HP
        character_id = create_character(self.campaign_id, self.user_id, name, char_class, stats["hp"])
        
        # Update character with generated stats
        update_character_stats(character_id, stats)
        
        # Create and return game session with the new character
        game_session = GameSession(self.campaign_id, self.username)
        game_session.character_id = character_id  # Set the ID
        game_session.load_character_stats()       # Load the character

        return game_session


class_options = ["Wizard", "Ranger", "Fighter"]