import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String

class NPC(SQLModel, table=True):
    __tablename__ = "npcs"

    
    npc_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    name: str
    class_: Optional[str] = Field(default=None, sa_column=Column("class", String))
    level: int = Field(default=1)
    hp: int = Field(default=10)
    max_hp: int = Field(default=10)
    ac: int = Field(default=10)
    strength: int = Field(default=10)
    dexterity: int = Field(default=10)
    constitution: int = Field(default=10)
    intelligence: int = Field(default=10)
    wisdom: int = Field(default=10)
    charisma: int = Field(default=10)
    current_location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.location_id")
    status: str = Field(default="alive")  # alive, dead, fled
    disposition: str = Field(default="neutral")  # friendly, hostile, neutral
    backstory: Optional[str] = None
    personality_traits: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    flaws: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    bonds: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    notable_abilities: Optional[str] = None
    relationships: Optional[str] = None
    lore: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    source_content_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        populate_by_name = True

