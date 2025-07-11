import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String

class Character(SQLModel, table=True):
    __tablename__ = "characters"
    
    character_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    name: str
    class_: Optional[str] = Field(default=None, sa_column=Column("class", String))
    level: int = Field(default=1)
    hp: int = Field(default=30)
    max_hp: int = Field(default=30)
    ac: int = Field(default=10)
    strength: int = Field(default=10)
    dexterity: int = Field(default=10)
    constitution: int = Field(default=10)
    intelligence: int = Field(default=10)
    wisdom: int = Field(default=10)
    charisma: int = Field(default=10)
    race: Optional[str] = None
    background: Optional[str] = None
    alignment: Optional[str] = None
    backstory: Optional[str] = None
    personality_traits: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    flaws: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    bonds: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    ideals: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    current_location_id: Optional[uuid.UUID] = None
    experience: int = Field(default=0)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        populate_by_name = True 