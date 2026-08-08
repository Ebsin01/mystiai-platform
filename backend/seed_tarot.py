import json
from pathlib import Path

from app.database import SessionLocal
from app.model.tarot_card import TarotCard

db = SessionLocal()

json_file = Path("data/tarot_cards.json")

with open(json_file, "r", encoding="utf-8") as f:
    cards = json.load(f)

try:
    for card in cards:
        exists = db.query(TarotCard).filter(
            TarotCard.name == card["name"]
        ).first()

        if exists:
            continue

        tarot = TarotCard(
            name=card["name"],
            arcana=card["arcana"],
            suit=card["suit"],
            upright_meaning=card["upright_meaning"],
            reversed_meaning=card["reversed_meaning"]
        )

        db.add(tarot)

    db.commit()
    print("Tarot cards inserted successfully!")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()