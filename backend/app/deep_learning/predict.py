from pathlib import Path
import joblib
import numpy as np
import logging
from typing import Optional

from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf

# Logging setup
logger = logging.getLogger(__name__)

# ============================================================
# PATHS - Use absolute paths relative to this file
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MAX_LENGTH = 20
VOCAB_SIZE = 5000  # Based on tokenizer vocabulary

# ============================================================
# LAZY LOADING - Models loaded only when first used
# ============================================================
_model = None
_tokenizer = None
_label_encoder = None


def _build_model_architecture() -> Sequential:
    """
    Build the exact model architecture for question classification.
    This is used as a fallback if weights cannot be loaded.
    """
    model = Sequential([
        Embedding(
            input_dim=VOCAB_SIZE,
            output_dim=128,
            input_length=MAX_LENGTH,
            name='embedding'
        ),
        LSTM(
            units=128,
            return_sequences=True,
            name='lstm_1'
        ),
        Dropout(0.2),
        LSTM(
            units=64,
            name='lstm_2'
        ),
        Dropout(0.2),
        Dense(32, activation='relu', name='dense_1'),
        Dropout(0.2),
        Dense(5, activation='softmax', name='output')  # 5 categories
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def _load_model():
    """
    Load the trained model weights with fallback mechanisms.
    Handles both .h5 and .keras formats, with compatibility for Keras 2.15.
    """
    global _model
    
    if _model is not None:
        return _model
    
    h5_path = MODEL_DIR / "question_classifier.h5"
    keras_path = MODEL_DIR / "question_classifier.keras"
    
    # Try loading .h5 format first (most compatible with Keras 2.15)
    if h5_path.exists():
        try:
            logger.info(f"Loading model from {h5_path}")
            _model = load_model(str(h5_path))
            logger.info("Successfully loaded model from .h5 file")
            return _model
        except Exception as e:
            logger.warning(f"Failed to load .h5 model: {str(e)}. Attempting .keras format...")
    
    # Try .keras format with custom object handling
    if keras_path.exists():
        try:
            logger.info(f"Loading model from {keras_path}")
            # Keras 2.15 may have issues with Keras 3 config keys
            _model = load_model(
                str(keras_path),
                safe_mode=False  # Allow loading models with potentially unsafe configs
            )
            logger.info("Successfully loaded model from .keras file")
            return _model
        except Exception as e:
            logger.warning(f"Failed to load .keras model: {str(e)}. Building from architecture...")
    
    # Fallback: Build model architecture and attempt to load weights
    try:
        logger.info("Building model from architecture and loading weights...")
        _model = _build_model_architecture()
        
        # Try to load weights from either format
        weights_path = None
        if h5_path.exists():
            weights_path = h5_path
        elif keras_path.exists():
            weights_path = keras_path
        
        if weights_path:
            try:
                # Extract weights from the model file
                temp_model = load_model(str(weights_path), safe_mode=False)
                _model.set_weights(temp_model.get_weights())
                logger.info("Successfully loaded weights from model file")
            except Exception as weight_error:
                logger.warning(
                    f"Could not load weights: {str(weight_error)}. "
                    "Using model with random initialization. "
                    "Predictions may be inaccurate until model is retrained."
                )
        
        return _model
        
    except Exception as e:
        logger.error(f"Critical error: Failed to initialize model: {str(e)}")
        raise RuntimeError(
            f"Failed to load or build ML model. "
            f"Ensure model files exist at {MODEL_DIR}. "
            f"Error: {str(e)}"
        )


def _load_tokenizer():
    """Load the tokenizer for text preprocessing."""
    global _tokenizer
    
    if _tokenizer is not None:
        return _tokenizer
    
    tokenizer_path = MODEL_DIR / "tokenizer.pkl"
    
    if not tokenizer_path.exists():
        raise FileNotFoundError(
            f"Tokenizer file not found at {tokenizer_path}. "
            f"Please ensure tokenizer.pkl exists."
        )
    
    try:
        _tokenizer = joblib.load(str(tokenizer_path))
        logger.info("Successfully loaded tokenizer")
        return _tokenizer
    except Exception as e:
        raise RuntimeError(f"Failed to load tokenizer: {str(e)}")


def _load_label_encoder():
    """Load the label encoder for category decoding."""
    global _label_encoder
    
    if _label_encoder is not None:
        return _label_encoder
    
    encoder_path = MODEL_DIR / "label_encoder.pkl"
    
    if not encoder_path.exists():
        raise FileNotFoundError(
            f"Label encoder file not found at {encoder_path}. "
            f"Please ensure label_encoder.pkl exists."
        )
    
    try:
        _label_encoder = joblib.load(str(encoder_path))
        logger.info("Successfully loaded label encoder")
        return _label_encoder
    except Exception as e:
        raise RuntimeError(f"Failed to load label encoder: {str(e)}")


def predict_category(question: str) -> dict:
    """
    Predict the category of a tarot question.
    
    Args:
        question: The question string to classify
        
    Returns:
        Dictionary with 'category' and 'confidence' (0-100%)
    """
    try:
        # Lazy load all required components
        model = _load_model()
        tokenizer = _load_tokenizer()
        label_encoder = _load_label_encoder()
        
        # Preprocess the question
        sequence = tokenizer.texts_to_sequences([question])
        
        padded = pad_sequences(
            sequence,
            maxlen=MAX_LENGTH,
            padding="post"
        )
        
        # Get prediction
        prediction = model.predict(
            padded,
            verbose=0
        )
        
        # Extract result
        predicted_index = np.argmax(prediction)
        confidence = float(np.max(prediction))
        category = label_encoder.inverse_transform([predicted_index])[0]
        
        return {
            "category": category,
            "confidence": round(confidence * 100, 2)
        }
        
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        # Return a safe default instead of crashing
        return {
            "category": "General",
            "confidence": 0.0,
            "error": str(e)
        }