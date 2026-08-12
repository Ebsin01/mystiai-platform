import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Fetch DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/palmistry_db")

# Convert postgres:// to postgresql:// for compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Use psycopg2 driver for better compatibility
if "postgresql://" in DATABASE_URL and "+psycopg2" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# IMPORTS MUST COME AFTER Base IS CREATED
from app.model.user import User
from app.model.palm_analysis import PalmAnalysis
from app.model.palm_interpretation import PalmInterpretation
from app.model.tarot_card import TarotCard
from app.model.three_card_reading import ThreeCardReading
from app.model.personality_report import PersonalityReport

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()