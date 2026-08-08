import cv2
import os
import numpy as np


# ==========================================
# PALM LINE DETECTION
# ==========================================

def detect_palm_lines(image_path, output_folder):

    # --------------------------------------
    # 1. Read original image
    # --------------------------------------
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # --------------------------------------
    # 2. Convert to grayscale
    # --------------------------------------
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------
    # 3. Improve contrast
    # --------------------------------------
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # --------------------------------------
    # 4. Reduce noise
    # --------------------------------------
    blurred = cv2.GaussianBlur(
        enhanced,
        (5, 5),
        0
    )

    # --------------------------------------
    # 5. Detect edges
    # --------------------------------------
    edges = cv2.Canny(
        blurred,
        30,
        100
    )

    # --------------------------------------
    # 6. Morphological closing
    # --------------------------------------
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    cleaned_edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    # --------------------------------------
    # 7. Detect line segments
    # --------------------------------------
    lines = cv2.HoughLinesP(
        cleaned_edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=40,
        maxLineGap=20
    )

    # --------------------------------------
    # 8. Create output image
    # --------------------------------------
    line_image = image.copy()

    if lines is not None:

        for line in lines:

            x1, y1, x2, y2 = line[0]

            cv2.line(
                line_image,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                2
            )

    # --------------------------------------
    # 9. Save outputs
    # --------------------------------------
    os.makedirs(
        output_folder,
        exist_ok=True
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "palm_edges.jpg"
        ),
        cleaned_edges
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "detected_palm_lines.jpg"
        ),
        line_image
    )

    print(
        "Palm line detection completed."
    )

    print(
        "Output saved to:"
    )

    print(
        output_folder
    )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    image_path = (
        r"C:\Users\Admin\Documents\AI-Palmistry-Tarot"
        r"\datasets\palmistry\001\001_F_L_32.JPG"
    )

    output_folder = (
        r"C:\Users\Admin\Documents\AI-Palmistry-Tarot"
        r"\datasets\palmistry\processed"
    )

    detect_palm_lines(
        image_path,
        output_folder
    )