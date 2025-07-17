import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Relationship(SQLModel, table=True):
    __tablename__ = "relationships"

    
    relationship_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    character_id: uuid.UUID = Field(foreign_key="characters.character_id")
    npc_id: uuid.UUID = Field(foreign_key="npcs.npc_id")
    relationship_type: str = Field(default="neutral")  # ally, enemy, neutral, romantic
    relationship_score: int = Field(default=0)  # -100 to +100
    history: Optional[str] = None
    last_interaction: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 