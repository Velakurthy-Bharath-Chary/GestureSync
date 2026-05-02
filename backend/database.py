import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

DATABASE_URL = os.getenv("DATABASE_URL")

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class GestureLog(Base):
    __tablename__ = "gesture_logs"

    id         = Column(Integer, primary_key=True)
    gesture    = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    action     = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()