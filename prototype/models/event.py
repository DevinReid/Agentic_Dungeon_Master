import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

class Event(SQLModel, table=True):
    __tablename__ = "events"

    
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    event_type: Optional[str] = None  # combat, conversation, discovery, etc.
    description: str
    location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.location_id")
    npcs_involved: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # JSONB array of NPC IDs
    characters_involved: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # JSONB array of character IDs
    player_actions: Optional[str] = None
    consequences: Optional[str] = None
    session_context: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 