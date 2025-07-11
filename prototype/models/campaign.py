import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Campaign(SQLModel, table=True):
    __tablename__ = "campaigns"

    
    campaign_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str] = None
    created_by: uuid.UUID = Field(foreign_key="users.user_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_played: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True 