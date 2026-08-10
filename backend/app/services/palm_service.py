import cv2
import numpy as np
import mediapipe as mp
import tempfile
import os
from pathlib import Path

from app.services.palm_analysis_engine import analyze_palm


# ============================================================
# MEDIAPIPE HAND LANDMARKER
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


# ============================================================
# CHECK MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"MediaPipe model not found: {MODEL_PATH}"
    )


# ============================================================
# CREATE MEDIAPIPE HAND LANDMARKER
# ============================================================

BaseOptions = mp.tasks.BaseOptions

HandLandmarker = (
    mp.tasks.vision.HandLandmarker
)

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)

RunningMode = (
    mp.tasks.vision.RunningMode
)


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


hand_landmarker = (
    HandLandmarker.create_from_options(
        options
    )
)


# ============================================================
# MAIN PALM PROCESSING FUNCTION
# ============================================================

def process_palm_image(image_bytes):

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
    # BASIC FEATURE EXTRACTION
    # --------------------------------------------------------

    palm_width = abs(
        index_finger.x
        - thumb.x
    )

    palm_length = abs(
        middle_finger.y
        - wrist.y
    )

    index_finger_length = abs(
        index_finger.y
        - wrist.y
    )

    middle_finger_length = abs(
        middle_finger.y
        - wrist.y
    )


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
        #
        # IMPORTANT:
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


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "hand_detected": True,

        "palm_features": {

            "palm_width": round(
                palm_width,
                4
            ),

            "palm_length": round(
                palm_length,
                4
            ),

            "index_finger_length": round(
                index_finger_length,
                4
            ),

            "middle_finger_length": round(
                middle_finger_length,
                4
            )
        },

        "palm_analysis": palm_analysis,

        "landmarks": landmarks
    }
