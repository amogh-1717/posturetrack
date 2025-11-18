from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import PostureRecord
from schemas import PostureRecordCreate
from datetime import datetime

def create_posture_record(db: Session, record: PostureRecordCreate):
    db_record = PostureRecord(
        status=record.status,
        timestamp=record.timestamp or datetime.utcnow()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_recent_records(db: Session, limit: int = 10):
    return db.query(PostureRecord).order_by(desc(PostureRecord.timestamp)).limit(limit).all()

def get_latest_record(db: Session):
    return db.query(PostureRecord).order_by(desc(PostureRecord.timestamp)).first()