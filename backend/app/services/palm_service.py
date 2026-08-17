import cv2
import numpy as np
import mediapipe as mp
import tempfile
import os
import logging
from pathlib import Path

from app.services.palm_analysis_engine import analyze_palm

# Logging setup
logger = logging.getLogger(__name__)

# ============================================================
# MEDIAPIPE HAND LANDMARKER - LAZY LOADING
# ============================================================

# Project structure:
#
# backend/
# ├── app/
# │   ├── models/
# │   │   └── hand_landmarker.task
# │   └── services/
# │       └── palm_service.py
#
# palm_service.py -> parents[2] = backend/

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "app"
    / "models"
    / "hand_landmarker.task"
)

# Global variable for lazy loading
_hand_landmarker = None
_mediapipe_ready = False


def _initialize_hand_landmarker():
    """
    Initialize the MediaPipe hand landmarker on first use.
    This is called lazily to avoid startup issues if the model file is missing.
    """
    global _hand_landmarker, _mediapipe_ready
    
    if _hand_landmarker is not None:
        return _hand_landmarker
    
    # Check if model exists
    if not MODEL_PATH.exists():
        error_msg = (
            f"MediaPipe model not found at {MODEL_PATH}. "
            f"The hand_landmarker.task file is required for palm analysis. "
            f"Please ensure the model file is present in the backend/app/models/ directory."
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        logger.info(f"Initializing MediaPipe hand landmarker from {MODEL_PATH}")
        
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode
        
        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(MODEL_PATH)
            ),
            running_mode=RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        _hand_landmarker = HandLandmarker.create_from_options(options)
        _mediapipe_ready = True
        logger.info("MediaPipe hand landmarker initialized successfully")
        return _hand_landmarker
        
    except Exception as e:
        error_msg = f"Failed to initialize MediaPipe hand landmarker: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def process_palm_image(image_bytes):
    """
    Process a palm image and extract landmarks using MediaPipe.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Dictionary with hand detection results and features
    """
    
    try:
        # Lazy load the hand landmarker
        hand_landmarker = _initialize_hand_landmarker()
        
        # --------------------------------------------------------
        # CONVERT BYTES TO IMAGE
        # --------------------------------------------------------

        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:
            return {
                "hand_detected": False,
                "message": "Invalid image"
            }


        height, width = image.shape[:2]
        image_height, image_width = int(height), int(width)

        # --------------------------------------------------------
        # CONVERT BGR -> RGB
        # --------------------------------------------------------

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )


        # --------------------------------------------------------
        # CREATE MEDIAPIPE IMAGE
        # --------------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_image
        )


        # --------------------------------------------------------
        # RUN HAND LANDMARK DETECTION
        # --------------------------------------------------------

        result = hand_landmarker.detect(
            mp_image
        )


        # --------------------------------------------------------
        # CHECK HAND DETECTION
        # --------------------------------------------------------

        if not result.hand_landmarks:
            logger.info("No hand detected in image")
            return {
                "hand_detected": False,
                "message": "No hand detected"
            }

        # --------------------------------------------------------
        # FIRST DETECTED HAND
        # --------------------------------------------------------

        hand_landmarks = result.hand_landmarks[0]


        # --------------------------------------------------------
        # EXTRACT 21 LANDMARKS
        # --------------------------------------------------------

        landmarks = []

        for index, landmark in enumerate(
            hand_landmarks
        ):

            landmarks.append({

                "id": index,

                "x": round(
                    landmark.x,
                    4
                ),

                "y": round(
                    landmark.y,
                    4
                ),

                "z": round(
                    landmark.z,
                    4
                )
            })


        # --------------------------------------------------------
        # IMPORTANT LANDMARKS
        # --------------------------------------------------------

        wrist = hand_landmarks[0]

        thumb = hand_landmarks[4]

        index_finger = hand_landmarks[8]

        middle_finger = hand_landmarks[12]


        # --------------------------------------------------------
        # BASIC FEATURE EXTRACTION (Scaled by image dimensions)
        # --------------------------------------------------------

        palm_width = abs(
            index_finger.x
            - thumb.x
        ) * image_width

        palm_length = abs(
            middle_finger.y
            - wrist.y
        ) * image_height

        index_finger_length = abs(
            index_finger.y
            - wrist.y
        ) * image_height

        middle_finger_length = abs(
            middle_finger.y
            - wrist.y
        ) * image_height


        # --------------------------------------------------------
        # TEMPORARY IMAGE FILE
        # --------------------------------------------------------

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        image_path = None

        try:

            temp_file.write(
                image_bytes
            )

            temp_file.close()

            image_path = temp_file.name


            # ----------------------------------------------------
            # RUN PALM ANALYSIS ENGINE
            # Pass MediaPipe landmarks to the engine.
            # ----------------------------------------------------

            palm_analysis = analyze_palm(
                image_path,
                landmarks
            )


        finally:

            if (
                image_path
                and os.path.exists(image_path)
            ):
                os.remove(image_path)
        
        # Return success response
        return {
            "hand_detected": True,
            "palm_features": {
                "image_width": image_width,
                "image_height": image_height,
                "palm_width": round(palm_width, 4),
                "palm_length": round(palm_length, 4),
                "index_finger_length": round(index_finger_length, 4),
                "middle_finger_length": round(middle_finger_length, 4)
            },
            "landmarks": landmarks,
            "palm_analysis": palm_analysis
        }
        
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        return {
            "hand_detected": False,
            "error": "Model file not found. Palm analysis is unavailable.",
            "details": str(e)
        }
    except RuntimeError as e:
        logger.error(f"MediaPipe initialization error: {str(e)}")
        return {
            "hand_detected": False,
            "error": "Failed to initialize hand detection model.",
            "details": str(e)
        }
    except Exception as e:
        logger.error(f"Error during palm image processing: {str(e)}")
        return {
            "hand_detected": False,
            "error": "An unexpected error occurred during palm analysis.",
            "details": str(e)
        }
