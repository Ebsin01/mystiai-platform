from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class TarotCard(Base):

    __tablename__ = "tarot_cards"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    arcana = Column(
        String,
        nullable=False
    )

    suit = Column(
        String,
        nullable=False
    )

    upright_meaning = Column(
        Text,
        nullable=False
    )

    reversed_meaning = Column(
        Text,
        nullable=False
    )