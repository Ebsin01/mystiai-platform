from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Maria15@localhost:5432/ai_palmistry"

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