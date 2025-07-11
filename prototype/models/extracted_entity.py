import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String

class ExtractedEntity(SQLModel, table=True):
    __tablename__ = "extracted_entities"

    
    entity_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    world_id: uuid.UUID = Field(foreign_key="worlds.world_id")
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    source_content_id: Optional[uuid.UUID] = Field(default=None, foreign_key="world_content.content_id")  # Where it was extracted from
    entity_type: str  # npc, location, organization, artifact, deity, threat
    entity_name: str
    description: Optional[str] = None
    status: str = Field(default="extracted")  # extracted, generated, detailed
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))  # AI-generated tags
    game_object_id: Optional[uuid.UUID] = None  # Links to actual NPC/location table when created
    extraction_context: Optional[str] = None  # The sentence it was extracted from
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 