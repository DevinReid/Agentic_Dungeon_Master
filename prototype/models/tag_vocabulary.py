import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class TagVocabulary(SQLModel, table=True):
    __tablename__ = "tag_vocabulary"

    
    tag_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    tag_name: str
    tag_category: Optional[str] = None  # entity, theme, category, location, relationship
    usage_count: int = Field(default=1)
    first_used: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 