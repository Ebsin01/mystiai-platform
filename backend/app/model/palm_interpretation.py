from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class PalmInterpretation(Base):
    __tablename__ = "palm_interpretations"

    id = Column(Integer, primary_key=True, index=True)

    analysis_id = Column(
        Integer,
        ForeignKey("palm_analyses.id"),
        nullable=False,
        unique=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    palm_shape = Column(String(50))

    personality_interpretation = Column(Text)
    career_interpretation = Column(Text)
    relationship_interpretation = Column(Text)
    life_interpretation = Column(Text)
    overall_interpretation = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
