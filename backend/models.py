from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class PostureRecord(Base):
    __tablename__ = "posture_records"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)  # "good" or "bad"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PostureRecord(id={self.id}, status='{self.status}', timestamp='{self.timestamp}')>"