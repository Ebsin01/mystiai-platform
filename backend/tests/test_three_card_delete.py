from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, Base, engine
from app.model.three_card_reading import ThreeCardReading
from app.model.user import User
from app.auth.jwt_handler import create_access_token


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_delete_three_card_reading_only_for_owner():
    db = SessionLocal()
    try:
        user = User(email='owner@example.com', full_name='Owner', password='hashed')
        db.add(user)
        db.commit()
        db.refresh(user)

        other_user = User(email='other@example.com', full_name='Other', password='hashed')
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        reading = ThreeCardReading(
            user_id=user.id,
            question='Will I prosper?',
            position='Past',
            card_id=1,
            card_name='The Fool',
            arcana='Major Arcana',
            suit='None',
            orientation='Upright',
            meaning='A new beginning'
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
    finally:
        db.close()

    owner_token = create_access_token({'sub': 'owner@example.com'})
    other_token = create_access_token({'sub': 'other@example.com'})

    owner_response = client.delete(f'/tarot/three-card-readings/{reading.id}', headers={'Authorization': f'Bearer {owner_token}'})
    assert owner_response.status_code == 200
    assert owner_response.json()['message'] == 'Three-card reading deleted successfully'

    db = SessionLocal()
    try:
        remaining = db.query(ThreeCardReading).filter(ThreeCardReading.id == reading.id).first()
        assert remaining is None
    finally:
        db.close()

    second_response = client.delete(f'/tarot/three-card-readings/{reading.id}', headers={'Authorization': f'Bearer {other_token}'})
    assert second_response.status_code == 404
