import cv2
import numpy as np
import mediapipe as mp
import tempfile
import os

from app.services.palm_analysis_engine import analyze_palm


# ============================================================
# MEDIAPIPE HAND DETECTION
# ============================================================

mp_hands = mp.solutions.hands


hands = mp_hands.Hands(

    static_image_mode=True,

    max_num_hands=1,

    min_detection_confidence=0.5

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
    # MEDIAPIPE PROCESSING
    # --------------------------------------------------------

    rgb_image = cv2.cvtColor(

        image,

        cv2.COLOR_BGR2RGB

    )


    result = hands.process(

        rgb_image

    )


    if not result.multi_hand_landmarks:

        return {

            "hand_detected": False,

            "message": "No hand detected"

        }


    hand_landmarks = (

        result.multi_hand_landmarks[0]

    )


    # --------------------------------------------------------
    # EXTRACT 21 LANDMARKS
    # --------------------------------------------------------

    landmarks = []


    for index, landmark in enumerate(

        hand_landmarks.landmark

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

    wrist = (

        hand_landmarks.landmark[0]

    )


    thumb = (

        hand_landmarks.landmark[4]

    )


    index_finger = (

        hand_landmarks.landmark[8]

    )


    middle_finger = (

        hand_landmarks.landmark[12]

    )


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


    temp_file.write(

        image_bytes

    )


    temp_file.close()


    image_path = temp_file.name


    # --------------------------------------------------------
    # RUN PALM ANALYSIS ENGINE
    # --------------------------------------------------------

    try:

        palm_analysis = analyze_palm(

            image_path

        )

    finally:

        if os.path.exists(

            image_path

        ):

            os.remove(

                image_path

            )


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