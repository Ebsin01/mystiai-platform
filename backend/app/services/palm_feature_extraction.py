import cv2
import numpy as np
import math


IMAGE_PATH = (
    r"C:\Users\Admin\Documents\AI-Palmistry-Tarot"
    r"\datasets\palmistry\001\001_F_L_32.JPG"
)


# ==========================================
# CALCULATE DISTANCE
# ==========================================

def calculate_distance(x1, y1, x2, y2):

    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )


# ==========================================
# CALCULATE ANGLE
# ==========================================

def calculate_angle(x1, y1, x2, y2):

    angle = math.degrees(
        math.atan2(
            y2 - y1,
            x2 - x1
        )
    )

    return abs(angle)


# ==========================================
# CLASSIFY LINE LENGTH
# ==========================================

def classify_line_length(
    length,
    image_width
):

    ratio = length / image_width

    if ratio < 0.25:

        return "Short"

    elif ratio < 0.50:

        return "Medium"

    else:

        return "Long"


# ==========================================
# CLASSIFY PALM SHAPE
# ==========================================

def classify_palm_shape(
    palm_width,
    palm_length
):

    ratio = palm_length / palm_width

    if ratio < 1.1:

        return "Square"

    elif ratio < 1.5:

        return "Rectangular"

    elif ratio >= 1.5:

        return "Long"

    else:

        return "Wide"


# ==========================================
# CLASSIFY HEAD LINE
# ==========================================

def classify_head_line(
    angle
):

    # Mostly horizontal = Straight
    if angle < 20 or angle > 160:

        return "Straight"

    return "Curved"


# ==========================================
# CONFIDENCE SCORE
# ==========================================

def calculate_confidence(
    detected_lines,
    expected_lines
):

    if detected_lines == 0:

        return 0.0

    confidence = (
        detected_lines /
        expected_lines
    )

    return round(
        min(confidence, 1.0),
        2
    )


# ==========================================
# EXTRACT PALM FEATURES
# ==========================================

def extract_palm_features(
    image_path
):

    image = cv2.imread(
        image_path
    )

    if image is None:

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    height, width = image.shape[:2]


    # ======================================
    # APPROXIMATE PALM MEASUREMENTS
    # ======================================

    palm_width = width * 0.60

    palm_length = height * 0.60


    # ======================================
    # PALM SHAPE
    # ======================================

    palm_shape = classify_palm_shape(

        palm_width,

        palm_length

    )


    # ======================================
    # GRAYSCALE
    # ======================================

    gray = cv2.cvtColor(

        image,

        cv2.COLOR_BGR2GRAY

    )


    # ======================================
    # BLUR
    # ======================================

    blurred = cv2.GaussianBlur(

        gray,

        (5, 5),

        0

    )


    # ======================================
    # EDGE DETECTION
    # ======================================

    edges = cv2.Canny(

        blurred,

        50,

        150

    )


    # ======================================
    # LINE DETECTION
    # ======================================

    lines = cv2.HoughLinesP(

        edges,

        1,

        np.pi / 180,

        threshold=50,

        minLineLength=30,

        maxLineGap=20

    )


    line_data = []


    if lines is not None:

        for line in lines:

            x1, y1, x2, y2 = line[0]


            length = calculate_distance(

                x1,

                y1,

                x2,

                y2

            )


            angle = calculate_angle(

                x1,

                y1,

                x2,

                y2

            )


            center_x = (

                x1 + x2

            ) / 2


            center_y = (

                y1 + y2

            ) / 2


            line_data.append({

                "length": length,

                "angle": angle,

                "center_x": center_x,

                "center_y": center_y

            })


    # ======================================
    # SORT LINES BY LENGTH
    # ======================================

    line_data.sort(

        key=lambda x: x["length"],

        reverse=True

    )


    # ======================================
    # DEFAULT VALUES
    # ======================================

    heart_line_length = 0

    head_line_length = 0

    life_line_length = 0

    head_line_angle = 0


    # ======================================
    # CLASSIFY CANDIDATE LINES
    # ======================================

    if len(line_data) >= 1:

        heart_line_length = (

            line_data[0]["length"]

        )


    if len(line_data) >= 2:

        head_line_length = (

            line_data[1]["length"]

        )

        head_line_angle = (

            line_data[1]["angle"]

        )


    if len(line_data) >= 3:

        life_line_length = (

            line_data[2]["length"]

        )


    # ======================================
    # LINE CLASSIFICATIONS
    # ======================================

    heart_line_classification = (

        classify_line_length(

            heart_line_length,

            width

        )

    )


    life_line_classification = (

        classify_line_length(

            life_line_length,

            width

        )

    )


    head_line_classification = (

        classify_head_line(

            head_line_angle

        )

    )


    # ======================================
    # CONFIDENCE
    # ======================================

    heart_confidence = (

        calculate_confidence(

            1 if heart_line_length > 0 else 0,

            1

        )

    )


    head_confidence = (

        calculate_confidence(

            1 if head_line_length > 0 else 0,

            1

        )

    )


    life_confidence = (

        calculate_confidence(

            1 if life_line_length > 0 else 0,

            1

        )

    )


    # ======================================
    # FINAL RESULT
    # ======================================

    return {

        "palm": {

            "width": round(

                palm_width,

                4

            ),

            "length": round(

                palm_length,

                4

            ),

            "shape": palm_shape

        },


        "heart_line": {

            "length": round(

                heart_line_length,

                4

            ),

            "classification":

                heart_line_classification,

            "confidence":

                heart_confidence

        },


        "head_line": {

            "length": round(

                head_line_length,

                4

            ),

            "classification":

                head_line_classification,

            "confidence":

                head_confidence

        },


        "life_line": {

            "length": round(

                life_line_length,

                4

            ),

            "classification":

                life_line_classification,

            "confidence":

                life_confidence

        }

    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    result = extract_palm_features(

        IMAGE_PATH

    )


    print("\n")

    print("=" * 50)

    print(

        "PALM FEATURE EXTRACTION RESULT"

    )

    print("=" * 50)


    print("\nPALM")

    print(

        "Width:",

        result["palm"]["width"]

    )

    print(

        "Length:",

        result["palm"]["length"]

    )

    print(

        "Shape:",

        result["palm"]["shape"]

    )


    print("\nHEART LINE")

    print(

        "Classification:",

        result["heart_line"]["classification"]

    )

    print(

        "Confidence:",

        result["heart_line"]["confidence"]

    )


    print("\nHEAD LINE")

    print(

        "Classification:",

        result["head_line"]["classification"]

    )

    print(

        "Confidence:",

        result["head_line"]["confidence"]

    )


    print("\nLIFE LINE")

    print(

        "Classification:",

        result["life_line"]["classification"]

    )

    print(

        "Confidence:",

        result["life_line"]["confidence"]

    )