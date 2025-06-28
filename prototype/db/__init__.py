# Database package for Agentic D&D
# Contains database operations and schema

from .db import *
from .db_schema import SCHEMA_SQL

__all__ = [
    # Database operations
    'get_or_create_user', 'create_campaign', 'list_campaigns', 'get_most_recent_campaign',
    'update_campaign_last_played', 'save_character', 'get_character', 'get_characters_for_user',
    'save_npc', 'get_npcs_at_location', 'save_event', 'get_recent_events', 
    'update_npc_relationship', 'get_npc_relationships',
    # Schema
    'SCHEMA_SQL'
] 