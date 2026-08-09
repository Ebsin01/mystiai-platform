from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import Base, engine

from app.routers import auth
from app.routers import palm

# Import models so SQLAlchemy knows about them
from app.model import user
from app.model import palm_analysis
from app.model import palm_interpretation
from app.model.tarot_card import TarotCard
from app.routers import tarot
from app.model.user import User
from app.model.palm_analysis import PalmAnalysis
from app.model.tarot_reading import TarotReading
from app.routers import reports
from app.model.three_card_reading import ThreeCardReading
from app.services.gemini_service import generate_ai_report
from app.routers import pdf
from app.routers import notifications

# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Palmistry & Tarot Intelligence Platform"
)


class AIModelInfoResponse(BaseModel):
    model_name: str
    framework: str
    test_accuracy: float
    categories: list[str]
    training_samples: int
    sequence_length: int
    tokenizer_words: int


# CORS configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Authentication routes
app.include_router(auth.router)


# Palm analysis routes
app.include_router(palm.router)
app.include_router(tarot.router)
app.include_router(reports.router)
app.include_router(pdf.router)
app.include_router(
    notifications.router
)


@app.get("/", summary="Health check")
def home():

    return {
        "message": "API Running Successfully"
    }


@app.get(
    "/ai/model-info",
    summary="Get AI model information",
    description="Return metadata for the tarot prediction model used by the application.",
    response_model=AIModelInfoResponse,
)
def get_ai_model_info():
    return AIModelInfoResponse(
        model_name="LSTM Neural Network",
        framework="TensorFlow 2.21.0",
        test_accuracy=100.0,
        categories=["Career", "Love", "Finance", "Health", "General"],
        training_samples=10000,
        sequence_length=20,
        tokenizer_words=5000,
    )
    
from sqlalchemy import text

@app.get("/debug")
def debug():
    with engine.connect() as conn:
        db = conn.execute(text("SELECT current_database()")).scalar()
        schema = conn.execute(text("SELECT current_schema()")).scalar()

        columns = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='palm_analyses'
            ORDER BY ordinal_position
        """)).fetchall()

    return {
        "database": db,
        "schema": schema,
        "columns": [c[0] for c in columns]
    }
@app.get("/test-gemini")
def test_gemini():

    scores = {
        "optimism": 85,
        "leadership": 78,
        "confidence": 82,
        "creativity": 90,
        "communication": 88,
        "decision_making": 75,
        "emotional_intelligence": 80,
        "stress_management": 70,
        "adaptability": 84,
        "risk_taking": 65,
        "emotional_balance": 79
    }

    return generate_ai_report(scores)