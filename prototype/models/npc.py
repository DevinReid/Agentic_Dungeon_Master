import uuid
from sqlmodel import Field, SQLModel

class NPC(SQLModel, table=True):
    npc_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id")
    name: str
    character_class: str
    level: int
    hp: int
    max_hp: int
    ac: int
    strength: int
    

    class Config:
        from_attributes = True

