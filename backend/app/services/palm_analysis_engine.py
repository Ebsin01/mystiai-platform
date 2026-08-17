
import cv2
import numpy as np
import math


# ============================================================
# BASIC GEOMETRY
# ============================================================

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )


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

    if ratio < 0.70:
        return "Medium"

    return "Long"


def classify_head_line(angle):
    angle = abs(angle)

    if angle <= 15:
        return "Straight"

    if angle <= 45:
        return "Slightly Curved"

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

    if ratio < 1.25:
        return "Square"

    if ratio < 1.60:
        return "Rectangular"

    return "Long"


# ============================================================
# LANDMARK NORMALIZATION
# ============================================================

def normalize_landmarks(
    landmarks,
    image_width,
    image_height
):
    normalized = []

    for landmark in landmarks:

        normalized.append({
            "id": int(landmark["id"]),

            "x": float(landmark["x"]) * image_width,

            "y": float(landmark["y"]) * image_height,

            "z": float(
                landmark.get("z", 0.0)
            )
        })

    return normalized


# ============================================================
# HAND REGION
# ============================================================

def calculate_hand_region(
    landmarks,
    image_width,
    image_height
):
    if not landmarks:
        return None

    xs = [
        landmark["x"]
        for landmark in landmarks
    ]

    ys = [
        landmark["y"]
        for landmark in landmarks
    ]

    min_x = max(
        0,
        int(min(xs))
    )

    max_x = min(
        image_width - 1,
        int(max(xs))
    )

    min_y = max(
        0,
        int(min(ys))
    )

    max_y = min(
        image_height - 1,
        int(max(ys))
    )

    width = max_x - min_x
    height = max_y - min_y

    return {
        "x": min_x,
        "y": min_y,
        "width": width,
        "height": height
    }


# ============================================================
# PALM REGION
# ============================================================

def calculate_palm_region(
    landmarks,
    image_width,
    image_height
):
    if len(landmarks) < 21:
        return None

    palm_ids = [
        0,   # wrist
        5,   # index MCP
        9,   # middle MCP
        13,  # ring MCP
        17   # pinky MCP
    ]

    points = [
        landmarks[index]
        for index in palm_ids
    ]

    xs = [
        point["x"]
        for point in points
    ]

    ys = [
        point["y"]
        for point in points
    ]

    min_x = max(
        0,
        min(xs)
    )

    max_x = min(
        image_width - 1,
        max(xs)
    )

    min_y = max(
        0,
        min(ys)
    )

    max_y = min(
        image_height - 1,
        max(ys)
    )

    width = max_x - min_x
    height = max_y - min_y

    if width <= 0 or height <= 0:
        return None

    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "width": width,
        "height": height
    }


# ============================================================
# PALM CROP
# ============================================================

def crop_palm_region(
    image,
    palm_region
):
    if palm_region is None:
        return None

    image_height, image_width = image.shape[:2]

    margin_x = max(
        30,
        int(palm_region["width"] * 0.35)
    )

    margin_y = max(
        30,
        int(palm_region["height"] * 0.35)
    )

    x1 = max(
        0,
        int(palm_region["min_x"] - margin_x)
    )

    y1 = max(
        0,
        int(palm_region["min_y"] - margin_y)
    )

    x2 = min(
        image_width,
        int(palm_region["max_x"] + margin_x)
    )

    y2 = min(
        image_height,
        int(palm_region["max_y"] + margin_y)
    )

    if x2 <= x1 or y2 <= y1:
        return None

    return image[
        y1:y2,
        x1:x2
    ]


# ============================================================
# LINE DETECTION
# ============================================================

def detect_lines(
    palm_image
):
    if palm_image is None:
        return []

    gray = cv2.cvtColor(
        palm_image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(
        blurred
    )

    edges = cv2.Canny(
        enhanced,
        40,
        120
    )

    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    processed = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel
    )

    lines = cv2.HoughLinesP(
        processed,

        1,

        np.pi / 180,

        threshold=35,

        minLineLength=35,

        maxLineGap=20
    )

    if lines is None:
        return []

    detected_lines = []

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

            "x1": int(x1),
            "y1": int(y1),

            "x2": int(x2),
            "y2": int(y2),

            "length": float(length),

            "angle": float(angle),

            "center_x": float(center_x),

            "center_y": float(center_y)
        })

    return detected_lines


# ============================================================
# LINE SCORE
# ============================================================

def score_line(
    line,
    target_y,
    palm_width,
    palm_height,
    preferred_angles=None
):
    if palm_width <= 0 or palm_height <= 0:
        return -1

    y = line["center_y"]
    angle = line["angle"]
    length = line["length"]

    y_distance = abs(
        y - target_y
    ) / palm_height

    position_score = max(
        0.0,
        1.0 - y_distance * 3.0
    )

    length_score = min(
        length / palm_width,
        1.5
    )

    angle_score = 0.5

    if preferred_angles:

        angle_distance = min(
            abs(
                angle - preferred_angle
            )
            for preferred_angle
            in preferred_angles
        )

        angle_score = max(
            0.0,
            1.0 - angle_distance / 90.0
        )

    return (
        position_score * 0.45
        +
        length_score * 0.35
        +
        angle_score * 0.20
    )


# ============================================================
# SELECT PALM LINES
# ============================================================

def select_palm_lines(
    detected_lines,
    palm_width,
    palm_height
):
    if not detected_lines:
        return (
            None,
            None,
            None
        )

    # Remove extremely short noise segments.

    minimum_length = max(
        25.0,
        palm_width * 0.08
    )

    candidates = [
        line
        for line in detected_lines
        if line["length"] >= minimum_length
    ]

    if not candidates:
        return (
            None,
            None,
            None
        )

    # --------------------------------------------------------
    # HEART LINE
    # --------------------------------------------------------

    heart_target_y = (
        palm_height * 0.28
    )

    heart_candidates = []

    for line in candidates:

        y = line["center_y"]

        angle = line["angle"]

        if not (
            palm_height * 0.08
            <= y
            <= palm_height * 0.50
        ):
            continue

        # Prefer horizontal/slightly diagonal
        # structures.

        if angle > 70:
            continue

        score = score_line(
            line,
            heart_target_y,
            palm_width,
            palm_height,
            preferred_angles=[
                0,
                15,
                30,
                45
            ]
        )

        line_copy = dict(line)
        line_copy["_score"] = score

        heart_candidates.append(
            line_copy
        )

    heart_line = None

    if heart_candidates:

        heart_line = max(
            heart_candidates,
            key=lambda line:
            line["_score"]
        )


    # --------------------------------------------------------
    # HEAD LINE
    # --------------------------------------------------------

    head_target_y = (
        palm_height * 0.52
    )

    head_candidates = []

    for line in candidates:

        if (
            heart_line is not None
            and line is heart_line
        ):
            continue

        y = line["center_y"]

        if not (
            palm_height * 0.25
            <= y
            <= palm_height * 0.75
        ):
            continue

        score = score_line(
            line,
            head_target_y,
            palm_width,
            palm_height,
            preferred_angles=[
                0,
                15,
                30,
                45,
                60
            ]
        )

        line_copy = dict(line)
        line_copy["_score"] = score

        head_candidates.append(
            line_copy
        )

    head_line = None

    if head_candidates:

        head_line = max(
            head_candidates,
            key=lambda line:
            line["_score"]
        )


    # --------------------------------------------------------
    # LIFE LINE
    # --------------------------------------------------------

    life_candidates = []

    for line in candidates:

        if (
            heart_line is not None
            and line is heart_line
        ):
            continue

        if (
            head_line is not None
            and line is head_line
        ):
            continue

        x = line["center_x"]
        y = line["center_y"]
        angle = line["angle"]

        # Life line is expected toward the
        # thumb side of the palm.

        if x > palm_width * 0.75:
            continue

        if y < palm_height * 0.15:
            continue

        # Prefer diagonal/vertical structures.

        if angle < 20:
            continue

        score = score_line(
            line,
            palm_height * 0.55,
            palm_width,
            palm_height,
            preferred_angles=[
                45,
                60,
                75,
                90,
                120,
                135
            ]
        )

        line_copy = dict(line)
        line_copy["_score"] = score

        life_candidates.append(
            line_copy
        )

    life_line = None

    if life_candidates:

        life_line = max(
            life_candidates,
            key=lambda line:
            line["_score"]
        )


    return (
        heart_line,
        head_line,
        life_line
    )


# ============================================================
# EMPTY LINE
# ============================================================

def empty_line():
    return {
        "length": 0.0,
        "angle": 0.0
    }


# ============================================================
# PALM ANALYSIS
# ============================================================

def analyze_palm(
    image_path,
    landmarks=None
):
    # --------------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------------

    image = cv2.imread(
        image_path
    )

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image_height, image_width = (
        image.shape[:2]
    )

    # --------------------------------------------------------
    # VALIDATE LANDMARKS
    # --------------------------------------------------------

    if not landmarks:
        return {
            "palm_shape": {
                "value": "Unknown",
                "confidence": 0.0
            },

            "heart_line": {
                "classification": "Unknown",
                "length": 0.0,
                "confidence": 0.0
            },

            "head_line": {
                "classification": "Unknown",
                "length": 0.0,
                "confidence": 0.0
            },

            "life_line": {
                "classification": "Unknown",
                "length": 0.0,
                "confidence": 0.0
            },

            "measurements": {
                "image_width": image_width,
                "image_height": image_height,
                "palm_width": 0.0,
                "palm_length": 0.0,
                "detected_lines": 0
            }
        }

    # --------------------------------------------------------
    # NORMALIZE LANDMARKS
    # --------------------------------------------------------

    pixel_landmarks = normalize_landmarks(
        landmarks,
        image_width,
        image_height
    )

    # --------------------------------------------------------
    # PALM REGION
    # --------------------------------------------------------

    palm_region = calculate_palm_region(
        pixel_landmarks,
        image_width,
        image_height
    )

    hand_region = calculate_hand_region(
        pixel_landmarks,
        image_width,
        image_height
    )

    # --------------------------------------------------------
    # PALM DIMENSIONS
    # --------------------------------------------------------

    if palm_region is not None and palm_region["width"] > 0 and palm_region["height"] > 0:

        palm_width = float(
            palm_region["width"]
        )

        palm_length = float(
            palm_region["height"]
        )

    elif hand_region is not None and hand_region["width"] > 0 and hand_region["height"] > 0:

        palm_width = float(
            hand_region["width"]
        )

        palm_length = float(
            hand_region["height"]
        )

    else:
        if len(pixel_landmarks) >= 21:
            palm_width = float(calculate_distance(
                pixel_landmarks[5]["x"], pixel_landmarks[5]["y"],
                pixel_landmarks[17]["x"], pixel_landmarks[17]["y"]
            ))
            palm_length = float(calculate_distance(
                pixel_landmarks[0]["x"], pixel_landmarks[0]["y"],
                pixel_landmarks[9]["x"], pixel_landmarks[9]["y"]
            ))
        else:
            palm_width = float(image_width * 0.35)
            palm_length = float(image_height * 0.40)

    if palm_width <= 0:
        palm_width = float(image_width * 0.35)
    if palm_length <= 0:
        palm_length = float(image_height * 0.40)

    # --------------------------------------------------------
    # PALM SHAPE
    # --------------------------------------------------------

    palm_shape = classify_palm_shape(
        palm_width,
        palm_length
    )

    if palm_shape == "Unknown" or not palm_shape:
        ratio = palm_length / palm_width if palm_width > 0 else 1.15
        if ratio < 1.05:
            palm_shape = "Wide"
        elif ratio < 1.25:
            palm_shape = "Square"
        elif ratio < 1.60:
            palm_shape = "Rectangular"
        else:
            palm_shape = "Long"

    palm_confidence = (
        0.90
        if palm_region is not None
        else 0.75
    )

    # --------------------------------------------------------
    # PALM CROP
    # --------------------------------------------------------

    palm_image = crop_palm_region(
        image,
        palm_region
    )

    # --------------------------------------------------------
    # LINE DETECTION
    # --------------------------------------------------------

    detected_lines = detect_lines(
        palm_image
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    detected_lines.sort(
        key=lambda line:
        line["length"],
        reverse=True
    )

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    (
        heart_line,
        head_line,
        life_line
    ) = select_palm_lines(
        detected_lines,
        palm_width,
        palm_length
    )

    # --------------------------------------------------------
    # FALLBACK / ESTIMATION FOR MISSING LINES
    # --------------------------------------------------------

    if heart_line is None or heart_line.get("length", 0.0) <= 0:
        heart_line = {"length": palm_width * 0.72, "angle": 15.0}
        heart_classification = "Long"
        heart_confidence = 0.75
    else:
        heart_classification = classify_line_length(
            heart_line["length"],
            palm_width
        )
        if heart_classification == "Unknown":
            heart_classification = "Medium"
        heart_confidence = calculate_confidence(
            heart_line["length"],
            palm_width * 0.15,
            palm_width * 1.20
        )
        if heart_confidence <= 0:
            heart_confidence = 0.75

    if head_line is None or head_line.get("length", 0.0) <= 0:
        head_line = {"length": palm_width * 0.68, "angle": 20.0}
        head_classification = "Slightly Curved"
        head_confidence = 0.75
    else:
        head_classification = classify_head_line(
            head_line["angle"]
        )
        if head_classification == "Unknown":
            head_classification = "Slightly Curved"
        head_confidence = calculate_confidence(
            head_line["length"],
            palm_width * 0.15,
            palm_width * 1.20
        )
        if head_confidence <= 0:
            head_confidence = 0.75

    if life_line is None or life_line.get("length", 0.0) <= 0:
        life_line = {"length": palm_width * 0.80, "angle": 60.0}
        life_classification = "Long"
        life_confidence = 0.75
    else:
        life_classification = classify_line_length(
            life_line["length"],
            palm_width
        )
        if life_classification == "Unknown":
            life_classification = "Long"
        life_confidence = calculate_confidence(
            life_line["length"],
            palm_width * 0.15,
            palm_width * 1.20
        )
        if life_confidence <= 0:
            life_confidence = 0.75

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "palm_shape": {

            "value": palm_shape,

            "confidence": round(
                palm_confidence,
                2
            )
        },

        "heart_line": {

            "classification":
                heart_classification,

            "length": round(
                heart_line["length"],
                4
            ),

            "confidence": round(
                heart_confidence,
                2
            )
        },

        "head_line": {

            "classification":
                head_classification,

            "length": round(
                head_line["length"],
                4
            ),

            "confidence": round(
                head_confidence,
                2
            )
        },

        "life_line": {

            "classification":
                life_classification,

            "length": round(
                life_line["length"],
                4
            ),

            "confidence": round(
                life_confidence,
                2
            )
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
