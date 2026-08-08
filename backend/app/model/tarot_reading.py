from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.database import Base


class TarotReading(Base):

    __tablename__ = "tarot_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    card_id = Column(
        Integer,
        ForeignKey("tarot_cards.id"),
        nullable=False
    )

    card_name = Column(
        String,
        nullable=False
    )

    suit = Column(
        String,
        nullable=False
    )

    orientation = Column(
        String,
        nullable=False
    )

    meaning = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )