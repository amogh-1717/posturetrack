from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - can be set via environment variable
# Make sure the port and host are explicit
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://posturetrackdatabase_user:posturetrack123@127.0.0.1:5432/posturetrackdatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()