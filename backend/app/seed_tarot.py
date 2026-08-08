from app.database import SessionLocal
from app.model.tarot_card import TarotCard


tarot_cards = [

    TarotCard(
        name="The Fool",
        arcana="Major Arcana",
        suit="Major Arcana",
        upright_meaning="New beginnings, adventure, freedom and taking a leap of faith.",
        reversed_meaning="Recklessness, poor decisions, fear of starting something new."
    ),

    TarotCard(
        name="The Magician",
        arcana="Major Arcana",
        suit="Major Arcana",
        upright_meaning="Skill, manifestation, confidence and using available resources.",
        reversed_meaning="Manipulation, lack of confidence and misuse of power."
    ),

    # Add your remaining cards here
]


db = SessionLocal()

try:

    for card in tarot_cards:

        existing_card = db.query(TarotCard).filter(
            TarotCard.name == card.name
        ).first()

        if existing_card:

            print(f"Already exists: {card.name}")

        else:

            db.add(card)

            print(f"Inserted: {card.name}")


    db.commit()

    print("Tarot cards seeding completed successfully!")


except Exception as e:

    db.rollback()

    print("Error:", e)


finally:

    db.close()