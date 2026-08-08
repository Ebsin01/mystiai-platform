from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship as orm_relationship

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

    # ==========================
    # Personality Scores
    # ==========================

    optimism = Column(Float)
    leadership = Column(Float)
    confidence = Column(Float)
    creativity = Column(Float)
    communication = Column(Float)
    decision_making = Column(Float)

    emotional_intelligence = Column(Float)
    stress_management = Column(Float)
    adaptability = Column(Float)
    risk_taking = Column(Float)
    emotional_balance = Column(Float)

    # ==========================
    # AI Report
    # ==========================

    personality_type = Column(Text)

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

    # ==========================
    # Relationships
    # ==========================

    analysis = orm_relationship(
        "PalmAnalysis",
        back_populates="report"
    )

    user = orm_relationship(
        "User",
        back_populates="reports"
    )