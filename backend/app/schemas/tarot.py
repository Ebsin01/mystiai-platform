from pydantic import BaseModel


class TarotCard(BaseModel):

    id: int

    name: str

    arcana: str

    suit: str

    orientation: str

    meaning: str


class TarotReadingRequest(BaseModel):

    card_id: int

    is_reversed: bool = False


class ThreeCardReadingRequest(BaseModel):

    question: str | None = None