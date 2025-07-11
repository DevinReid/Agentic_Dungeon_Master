import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String, JSON

class Location(SQLModel, table=True):
    __tablename__ = "locations"

    location_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    name: str
    description: Optional[str] = None
    connections: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # JSONB array of connected location IDs
    notable_features: Optional[str] = None
    location_type: Optional[str] = None  # temple/city/dungeon/forest/cave/etc
    size: Optional[str] = None  # small/medium/large
    inhabitants: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))  # Array of inhabitant types
    notable_items: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))  # Array of notable items
    atmosphere: Optional[str] = None  # Description of the atmosphere
    relationships: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Array of relationships
    lore: Optional[str] = None  # Historical lore
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    source_content_type: Optional[str] = None  # Where this location was extracted from
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 