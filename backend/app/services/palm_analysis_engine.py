import cv2
import numpy as np
import math


# ============================================================
# DISTANCE
# ============================================================

def calculate_distance(x1, y1, x2, y2):

    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )


# ============================================================
# ANGLE
# ============================================================

def calculate_angle(x1, y1, x2, y2):

    angle = math.degrees(
        math.atan2(
            y2 - y1,
            x2 - x1
        )
    )

    return abs(angle)


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    detected_value,
    expected_min,
    expected_max
):

    if detected_value <= 0:

        return 0.0

    if expected_min <= detected_value <= expected_max:

        return 0.90

    return 0.60


# ============================================================
# LINE CLASSIFICATION
# ============================================================

def classify_line_length(
    length,
    palm_width
):

    if palm_width <= 0:

        return "Unknown"

    ratio = length / palm_width


    if ratio < 0.35:

        return "Short"

    elif ratio < 0.70:

        return "Medium"

    else:

        return "Long"


# ============================================================
# HEAD LINE CLASSIFICATION
# ============================================================

def classify_head_line(
    angle
):

    angle = abs(angle)


    if angle <= 15:

        return "Straight"

    elif angle <= 45:

        return "Slightly Curved"

    else:

        return "Curved"


# ============================================================
# PALM SHAPE
# ============================================================

def classify_palm_shape(
    palm_width,
    palm_height
):

    if palm_width <= 0:

        return "Unknown"


    ratio = palm_height / palm_width


    if ratio < 1.05:

        return "Wide"

    elif ratio < 1.25:

        return "Square"

    elif ratio < 1.60:

        return "Rectangular"

    else:

        return "Long"


# ============================================================
# FIND HAND CONTOUR
# ============================================================

def find_hand_contour(
    image
):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )


    _, threshold = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY_INV +
        cv2.THRESH_OTSU
    )


    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    if not contours:

        return None


    largest_contour = max(
        contours,
        key=cv2.contourArea
    )


    return largest_contour


# ============================================================
# PALM ANALYSIS ENGINE
# ============================================================

def analyze_palm(
    image_path
):

    image = cv2.imread(
        image_path
    )


    if image is None:

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    image_height, image_width = image.shape[:2]


    # ========================================================
    # PREPROCESSING
    # ========================================================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )


    # ========================================================
    # CLAHE
    # ========================================================

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )


    enhanced = clahe.apply(
        blurred
    )


    # ========================================================
    # EDGE DETECTION
    # ========================================================

    edges = cv2.Canny(
        enhanced,
        50,
        150
    )


    # ========================================================
    # MORPHOLOGICAL PROCESSING
    # ========================================================

    kernel = np.ones(
        (3, 3),
        np.uint8
    )


    processed = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel
    )


    # ========================================================
    # ACTUAL HAND CONTOUR
    # ========================================================

    contour = find_hand_contour(
        image
    )


    if contour is not None:

        x, y, w, h = cv2.boundingRect(
            contour
        )


        palm_width = float(w)

        palm_length = float(h)


    else:

        palm_width = image_width * 0.60

        palm_length = image_height * 0.60


    # ========================================================
    # PALM SHAPE
    # ========================================================

    palm_shape = classify_palm_shape(
        palm_width,
        palm_length
    )


    # ========================================================
    # LINE DETECTION
    # ========================================================

    lines = cv2.HoughLinesP(

        processed,

        1,

        np.pi / 180,

        threshold=30,

        minLineLength=30,

        maxLineGap=30

    )


    detected_lines = []


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


            detected_lines.append({

                "x1": x1,

                "y1": y1,

                "x2": x2,

                "y2": y2,

                "length": length,

                "angle": angle,

                "center_x": center_x,

                "center_y": center_y

            })


    # ========================================================
    # SORT LINES BY LENGTH
    # ========================================================

    detected_lines.sort(

        key=lambda line:

        line["length"],

        reverse=True

    )


    # ========================================================
    # SELECT LINES BASED ON IMAGE POSITION
    # ========================================================

    heart_line = None

    head_line = None

    life_line = None


    for line in detected_lines:

        center_y = line["center_y"]

        center_x = line["center_x"]


        # Upper area = possible heart line

        if (

            heart_line is None

            and center_y < image_height * 0.45

        ):

            heart_line = line


        # Middle area = possible head line

        elif (

            head_line is None

            and image_height * 0.35

            <= center_y

            <= image_height * 0.70

        ):

            head_line = line


        # Lower/side area = possible life line

        elif (

            life_line is None

            and center_y > image_height * 0.45

        ):

            life_line = line


    # ========================================================
    # FALLBACK
    # ========================================================

    if heart_line is None:

        heart_line = {

            "length": 0,

            "angle": 0

        }


    if head_line is None:

        head_line = {

            "length": 0,

            "angle": 0

        }


    if life_line is None:

        life_line = {

            "length": 0,

            "angle": 0

        }


    # ========================================================
    # CLASSIFICATION
    # ========================================================

    heart_classification = classify_line_length(

        heart_line["length"],

        palm_width

    )


    head_classification = classify_head_line(

        head_line["angle"]

    )


    life_classification = classify_line_length(

        life_line["length"],

        palm_width

    )


    # ========================================================
    # CONFIDENCE
    # ========================================================

    heart_confidence = calculate_confidence(

        heart_line["length"],

        palm_width * 0.20,

        palm_width * 1.20

    )


    head_confidence = calculate_confidence(

        head_line["length"],

        palm_width * 0.20,

        palm_width * 1.20

    )


    life_confidence = calculate_confidence(

        life_line["length"],

        palm_width * 0.20,

        palm_width * 1.20

    )


    palm_confidence = (

        0.90

        if contour is not None

        else 0.60

    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "palm_shape": {

            "value": palm_shape,

            "confidence": palm_confidence

        },


        "heart_line": {

            "classification":

                heart_classification,

            "length":

                round(

                    heart_line["length"],

                    4

                ),

            "confidence":

                heart_confidence

        },


        "head_line": {

            "classification":

                head_classification,

            "length":

                round(

                    head_line["length"],

                    4

                ),

            "confidence":

                head_confidence

        },


        "life_line": {

            "classification":

                life_classification,

            "length":

                round(

                    life_line["length"],

                    4

                ),

            "confidence":

                life_confidence

        },


        "measurements": {

            "image_width":

                image_width,

            "image_height":

                image_height,

            "palm_width":

                round(

                    palm_width,

                    4

                ),

            "palm_length":

                round(

                    palm_length,

                    4

                ),

            "detected_lines":

                len(detected_lines)

        }

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    image_path = (

        r"C:\Users\Admin\Documents"

        r"\AI-Palmistry-Tarot"

        r"\datasets\palmistry"

        r"\001"

        r"\001_F_L_32.JPG"

    )


    result = analyze_palm(

        image_path

    )


    print("\n")

    print("=" * 60)

    print("PALM ANALYSIS RESULT")

    print("=" * 60)


    print("\nPALM SHAPE")

    print(

        result["palm_shape"]

    )


    print("\nHEART LINE")

    print(

        result["heart_line"]

    )


    print("\nHEAD LINE")

    print(

        result["head_line"]

    )


    print("\nLIFE LINE")

    print(

        result["life_line"]

    )


    print("\nMEASUREMENTS")

    print(

        result["measurements"]

    )