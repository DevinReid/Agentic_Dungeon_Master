import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String, JSON

class WorldContent(SQLModel, table=True):
    __tablename__ = "world_content"

    
    content_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    parent_content_id: Optional[uuid.UUID] = Field(default=None, foreign_key="world_content.content_id")  # For hierarchical content (expansions)
    world_id: uuid.UUID = Field(foreign_key="worlds.world_id")
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    source_type: str  # universe_builder, expansion_bot, regional_builder, manual
    content_type: str  # world_overview, magic_system, pantheon, global_threats, political_structure, regional_overview
    title: str
    content: str  # The full paragraph/essay content
    content_metadata: Optional[dict] = Field(default=None, sa_column=Column("metadata", JSON))  # Structured data (UniverseBuilder JSON objects)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))  # AI-generated tags for cross-referencing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 