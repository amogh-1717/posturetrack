from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostureRecordCreate(BaseModel):
    status: str
    timestamp: Optional[datetime] = None

class PostureRecord(BaseModel):
    id: int
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PostureUpdate(BaseModel):
    status: str
    timestamp: str  # ISO format string for WebSocket transmission