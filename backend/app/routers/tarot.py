from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from pydantic import BaseModel
from datetime import datetime
import random

from app.database import get_db
from app.auth.dependencies import get_current_user

from app.model.tarot_card import TarotCard
from app.model.tarot_reading import TarotReading
from app.model.three_card_reading import ThreeCardReading
from app.services.ai_interpreter import generate_three_card_interpretation
from app.services.personality_analyzer import analyze_personality
from app.services.life_trends import analyze_life_trends
from app.services.recommendation_engine import generate_recommendations
from app.deep_learning.predict import predict_category
from app.deep_learning.predict import predict_category


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/tarot",
    tags=["Tarot"]
)


# =====================================================
# REQUEST MODEL - SINGLE CARD READING
# =====================================================

class TarotReadingRequest(BaseModel):

    card_id: int

    is_reversed: bool = False


# =====================================================
# REQUEST MODEL - THREE CARD READING
# =====================================================

class ThreeCardReadingRequest(BaseModel):

    question: str | None = None

    card_ids: list[int] | None = None

    cards: list[int] | None = None


# =====================================================
# RESPONSE MODEL - SINGLE CARD
# =====================================================

class TarotReadingResponse(BaseModel):

    reading_id: int

    card_id: int

    card_name: str

    suit: str

    orientation: str

    meaning: str | None

    created_at: datetime


# =====================================================
# 1. GET ALL TAROT CARDS
# =====================================================

@router.get("/cards")
def get_tarot_cards(

    db: Session = Depends(get_db)

):

    cards = db.query(

        TarotCard

    ).all()


    return cards


# =====================================================
# 2. DRAW RANDOM TAROT CARD
# =====================================================

@router.get("/draw")
def draw_tarot_card(

    db: Session = Depends(get_db)

):

    card = db.query(

        TarotCard

    ).order_by(

        func.random()

    ).first()


    if not card:

        raise HTTPException(

            status_code=404,

            detail="No tarot cards found"

        )


    return card


# =====================================================
# 3. SAVE SINGLE TAROT READING
# =====================================================

@router.post("/readings")
def save_tarot_reading(

    reading_data: TarotReadingRequest,

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    # Find card
    card = db.query(

        TarotCard

    ).filter(

        TarotCard.id == reading_data.card_id

    ).first()


    if not card:

        raise HTTPException(

            status_code=404,

            detail="Tarot card not found"

        )


    # Determine orientation
    if reading_data.is_reversed:

        orientation = "Reversed"

        meaning = card.reversed_meaning

    else:

        orientation = "Upright"

        meaning = card.upright_meaning


    # Create reading
    new_reading = TarotReading(

        user_id=current_user.id,

        card_id=card.id,

        card_name=card.name,

        suit=(

            card.suit

            or card.arcana

            or "Major Arcana"

        ),

        orientation=orientation,

        meaning=meaning

    )


    # Save
    db.add(new_reading)

    db.commit()

    db.refresh(new_reading)


    return {

        "message":

            "Tarot reading saved successfully",

        "reading_id":

            new_reading.id,

        "card_id":

            new_reading.card_id,

        "card_name":

            new_reading.card_name,

        "suit":

            new_reading.suit,

        "orientation":

            new_reading.orientation,

        "meaning":

            new_reading.meaning,

        "created_at":

            new_reading.created_at

    }


# =====================================================
# 4. GET MY TAROT READING HISTORY
# =====================================================

@router.get(

    "/readings",

    response_model=list[TarotReadingResponse]

)

def get_my_readings(

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    readings = db.query(

        TarotReading

    ).filter(

        TarotReading.user_id

        == current_user.id

    ).order_by(

        TarotReading.created_at.desc()

    ).all()


    result = []


    for reading in readings:

        result.append({

            "reading_id":

                reading.id,

            "card_id":

                reading.card_id,

            "card_name":

                reading.card_name,

            "suit":

                reading.suit,

            "orientation":

                reading.orientation,

            "meaning":

                reading.meaning,

            "created_at":

                reading.created_at

        })


    return result


# =====================================================
# 5. GET SINGLE TAROT READING
# =====================================================

@router.get(

    "/readings/{reading_id}",

    response_model=TarotReadingResponse

)

def get_single_reading(

    reading_id: int,

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    reading = db.query(

        TarotReading

    ).filter(

        TarotReading.id == reading_id,

        TarotReading.user_id == current_user.id

    ).first()


    if not reading:

        raise HTTPException(

            status_code=404,

            detail="Reading not found"

        )


    return {

        "reading_id":

            reading.id,

        "card_id":

            reading.card_id,

        "card_name":

            reading.card_name,

        "suit":

            reading.suit,

        "orientation":

            reading.orientation,

        "meaning":

            reading.meaning,

        "created_at":

            reading.created_at

    }


# =====================================================
# 6. THREE CARD TAROT READING
# =====================================================

@router.post(

    "/three-card-reading"

)

def three_card_reading(

    reading_data: ThreeCardReadingRequest,

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)

):

    # Deep Learning Prediction
    prediction = predict_category(
        reading_data.question
    )

    # Get all tarot cards
    cards = db.query(
        TarotCard
    ).all()

    # Auto-seed default cards if DB has < 3 cards
    if len(cards) < 3:
        default_cards = [
            TarotCard(name="The Fool", arcana="Major Arcana", suit="Trump", upright_meaning="New beginnings, innocence, spontaneity", reversed_meaning="Recklessness, risk-taking, risk"),
            TarotCard(name="The Magician", arcana="Major Arcana", suit="Trump", upright_meaning="Manifestation, resourcefulness, power", reversed_meaning="Illusion, manipulation, unused ability"),
            TarotCard(name="The High Priestess", arcana="Major Arcana", suit="Trump", upright_meaning="Intuition, sacred knowledge, divine feminine", reversed_meaning="Secrets, disconnected intuition, withdrawal"),
            TarotCard(name="The Empress", arcana="Major Arcana", suit="Trump", upright_meaning="Femininity, beauty, nature, abundance", reversed_meaning="Creative block, dependence on others"),
            TarotCard(name="The Emperor", arcana="Major Arcana", suit="Trump", upright_meaning="Authority, establishment, structure, father figure", reversed_meaning="Domination, excessive control, lack of discipline"),
            TarotCard(name="The Hierophant", arcana="Major Arcana", suit="Trump", upright_meaning="Spiritual wisdom, religious beliefs, conformity", reversed_meaning="Personal beliefs, freedom, challenging status quo"),
            TarotCard(name="The Lovers", arcana="Major Arcana", suit="Trump", upright_meaning="Love, harmony, relationships, values alignment", reversed_meaning="Self-love, disharmony, imbalance, misalignment"),
            TarotCard(name="The Chariot", arcana="Major Arcana", suit="Trump", upright_meaning="Control, willpower, success, action, determination", reversed_meaning="Self-doubt, lack of direction, loss of control"),
        ]
        for dc in default_cards:
            existing = db.query(TarotCard).filter(TarotCard.name == dc.name).first()
            if not existing:
                db.add(dc)
        db.commit()
        cards = db.query(TarotCard).all()

    # Select 3 cards based on requested card_ids/cards or random selection
    requested_ids = reading_data.card_ids or reading_data.cards or []
    selected_cards = []
    if requested_ids and len(requested_ids) >= 3:
        card_map = {c.id: c for c in cards}
        for cid in requested_ids[:3]:
            if cid in card_map and card_map[cid] not in selected_cards:
                selected_cards.append(card_map[cid])

    if len(selected_cards) < 3:
        remaining_cards = [c for c in cards if c not in selected_cards]
        if not remaining_cards:
            remaining_cards = cards
        needed = 3 - len(selected_cards)
        if len(remaining_cards) >= needed:
            selected_cards.extend(random.sample(remaining_cards, needed))
        else:
            selected_cards.extend(remaining_cards)
        while len(selected_cards) < 3 and selected_cards:
            selected_cards.append(selected_cards[0])


    # Positions
    positions = [

        "Past",

        "Present",

        "Future"

    ]


    readings = []


    # Generate reading
    for card, position in zip(

        selected_cards,

        positions

    ):

        # Random orientation
        is_reversed = random.choice(

            [

                True,

                False

            ]

        )


        if is_reversed:

            orientation = "Reversed"

            meaning = card.reversed_meaning

        else:

            orientation = "Upright"

            meaning = card.upright_meaning


        # Save reading
        saved_reading = ThreeCardReading(

            user_id=current_user.id,

            question=reading_data.question,
            


            position=position,

            card_id=card.id,

            card_name=card.name,

            arcana=card.arcana,

            suit=card.suit,

            orientation=orientation,

            meaning=meaning

        )


        db.add(

            saved_reading

        )


        # Add response
        readings.append({

            "position": position,

            "card_id": card.id,

            "card_name": card.name,

            "arcana": card.arcana,

            "suit": card.suit,

            "orientation": orientation,

            "meaning": meaning

        })



    # Save all 3 cards
    db.commit()

    ai_interpretation = generate_three_card_interpretation(
        reading_data.question,
        readings
    )

    personality = analyze_personality(readings)

    life_trends = analyze_life_trends(readings)
    recommendations = generate_recommendations(
    reading_data.question,
    readings
)

    return {
    "message": "Three-card reading generated successfully",
    "reading_type": "Three Card Spread",
    "question": reading_data.question,

    "predicted_category": prediction["category"],
    "prediction_confidence": prediction["confidence"],

    "cards": readings,

    "ai_interpretation": ai_interpretation,

    "personality": personality,

    "life_trends": life_trends,

    "recommendations": recommendations
}


# =====================================================
# 7. GET THREE-CARD READING HISTORY
# =====================================================

@router.get(

    "/three-card-readings"

)

def get_three_card_readings(

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    readings = db.query(

        ThreeCardReading

    ).filter(

        ThreeCardReading.user_id

        == current_user.id

    ).order_by(

        ThreeCardReading.created_at.desc()

    ).all()


    return {

        "count": len(readings),

        "readings": readings

    }


# =====================================================
# 8. GET ONE THREE-CARD READING
# =====================================================

@router.get(

    "/three-card-readings/{reading_id}",

    summary="Get a specific three-card reading",

    description="Retrieve one three-card reading belonging to the authenticated user.",

    tags=["Tarot"]

)
def get_three_card_reading(

    reading_id: int,

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    reading = db.query(

        ThreeCardReading

    ).filter(

        ThreeCardReading.id == reading_id,

        ThreeCardReading.user_id == current_user.id

    ).first()


    if not reading:

        raise HTTPException(

            status_code=404,

            detail="Three-card reading not found"

        )


    return reading


# =====================================================
# 9. DELETE ONE THREE-CARD READING
# =====================================================

@router.delete(

    "/three-card-readings/{reading_id}",

    summary="Delete a three-card reading",

    description="Delete a three-card reading by ID. Only the authenticated owner can delete their own reading.",

    tags=["Tarot"]

)
def delete_three_card_reading(

    reading_id: int,

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(

        get_db

    )

):

    reading = db.query(

        ThreeCardReading

    ).filter(

        ThreeCardReading.id == reading_id,

        ThreeCardReading.user_id == current_user.id

    ).first()


    if not reading:

        raise HTTPException(

            status_code=404,

            detail="Three-card reading not found"

        )


    db.delete(reading)

    db.commit()


    return {

        "message": "Three-card reading deleted successfully",

        "reading_id": reading_id

    }