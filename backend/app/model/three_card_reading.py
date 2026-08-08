from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database import Base


class ThreeCardReading(Base):

    __tablename__ = "three_card_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    question = Column(
        Text,
        nullable=True
    )

    position = Column(
        String,
        nullable=False
    )

    card_id = Column(
        Integer,
        nullable=False
    )

    card_name = Column(
        String,
        nullable=False
    )

    arcana = Column(
        String,
        nullable=False
    )

    suit = Column(
        String,
        nullable=True
    )

    orientation = Column(
        String,
        nullable=False
    )

    meaning = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )