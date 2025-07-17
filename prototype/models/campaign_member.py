import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel

class CampaignMember(SQLModel, table=True):
    __tablename__ = "campaign_members"
    
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", primary_key=True)
    role: str = Field(default="player")  # dm, player
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 