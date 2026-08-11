from pathlib import Path
import joblib
import numpy as np

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

model = load_model(MODEL_DIR / "question_classifier.h5")
tokenizer = joblib.load(MODEL_DIR / "tokenizer.pkl")
label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")

MAX_LENGTH = 20


def predict_category(question: str):
    sequence = tokenizer.texts_to_sequences([question])

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LENGTH,
        padding="post"
    )

    prediction = model.predict(
        padded,
        verbose=0
    )

    predicted_index = np.argmax(prediction)

    confidence = float(np.max(prediction))

    category = label_encoder.inverse_transform(
        [predicted_index]
    )[0]

    return {
        "category": category,
        "confidence": round(confidence * 100, 2)
    }