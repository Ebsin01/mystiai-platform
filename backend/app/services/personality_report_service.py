from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database import Base


class PersonalityReport(Base):

    __tablename__ = "personality_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    analysis_id = Column(
        Integer,
        ForeignKey("palm_analyses.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    optimism = Column(Float)

    leadership = Column(Float)

    confidence = Column(Float)

    creativity = Column(Float)

    communication = Column(Float)

    decision_making = Column(Float)

    emotional_balance = Column(Float)

    strengths = Column(Text)

    weaknesses = Column(Text)

    career = Column(Text)

    relationship = Column(Text)

    health = Column(Text)

    summary = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )