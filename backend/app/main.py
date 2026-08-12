import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text

# Logging setup
logger = logging.getLogger(__name__)

# Database imports
from app.database import Base, engine 

# Import models so SQLAlchemy registers them before table creation
from app.model import user, palm_analysis, palm_interpretation
from app.model.tarot_card import TarotCard
from app.model.user import User
from app.model.palm_analysis import PalmAnalysis
from app.model.tarot_reading import TarotReading
from app.model.three_card_reading import ThreeCardReading

# Import routers & services
from app.routers import auth, palm, tarot, reports, pdf, notifications
from app.services.gemini_service import generate_ai_report

# 1. Create database tables on startup (with graceful fallback)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error(f"Database connection error: {e}")
    logger.warning("Continuing startup despite database error - database may be temporarily unavailable")

# 2. Instantiate FastAPI app (Single instance)
app = FastAPI(title="Palmistry & Tarot Intelligence Platform")

# 3. CORS Configuration - Environment-based
def _get_cors_origins() -> list:
    """
    Get allowed CORS origins from environment variables or use defaults.
    
    Environment variable: CORS_ORIGINS (comma-separated list)
    Defaults to localhost origins for development
    """
    cors_env = os.getenv("CORS_ORIGINS")
    
    if cors_env:
        # Parse comma-separated list
        origins = [origin.strip() for origin in cors_env.split(",")]
        logger.info(f"CORS configured with {len(origins)} origins from environment")
        return origins
    else:
        # Default to localhost for development
        defaults = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ]
        logger.warning(
            "CORS_ORIGINS environment variable not set. "
            f"Using development defaults: {defaults}"
        )
        return defaults

origins = _get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS middleware configured with {len(origins)} allowed origins")

# 4. Include Routers
app.include_router(auth.router)
app.include_router(palm.router)
app.include_router(tarot.router)
app.include_router(reports.router)
app.include_router(pdf.router)
app.include_router(notifications.router)

# 5. Pydantic Models
class AIModelInfoResponse(BaseModel):
    model_name: str
    framework: str
    test_accuracy: float
    categories: list[str]
    training_samples: int
    sequence_length: int
    tokenizer_words: int

# 6. Routes
@app.get("/", summary="Health check")
def home():
    return {"status": "ok", "message": "API Running Successfully"}

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

# 7. Local Execution Execution Block (Must be at the very bottom)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)