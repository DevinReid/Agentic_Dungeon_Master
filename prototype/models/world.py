import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

class World(SQLModel, table=True):
    __tablename__ = "worlds"

    
    world_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    world_name: str
    scope: str  # intimate, regional, continental, planetary
    theme_list: Optional[str] = None  # magic, adventure, political intrigue
    region_count: int = Field(default=1)
    major_city_count: int = Field(default=1)
    settlement_count: int = Field(default=3)
    magic_level: str = Field(default="medium")  # none, low, medium, high
    full_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Full universe/world JSON for backup/versioning
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 