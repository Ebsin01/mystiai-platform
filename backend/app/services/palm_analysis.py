import cv2
import os


# ==========================================
# PALM IMAGE PREPROCESSING
# ==========================================

def preprocess_palm_image(image_path):

    # --------------------------------------
    # 1. Read image
    # --------------------------------------
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # --------------------------------------
    # 2. Convert to Grayscale
    # --------------------------------------
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------
    # 3. Gaussian Blur
    # --------------------------------------
    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # --------------------------------------
    # 4. CLAHE
    # --------------------------------------
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(blurred)

    # --------------------------------------
    # 5. Thresholding
    # --------------------------------------
    _, threshold = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # --------------------------------------
    # 6. Canny Edge Detection
    # --------------------------------------
    edges = cv2.Canny(
        enhanced,
        50,
        150
    )

    # --------------------------------------
    # 7. Morphological Operations
    # --------------------------------------
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    morphed = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    return {
        "original": image,
        "gray": gray,
        "blurred": blurred,
        "enhanced": enhanced,
        "threshold": threshold,
        "edges": edges,
        "morphed": morphed
    }


# ==========================================
# SAVE OUTPUT IMAGES
# ==========================================

def save_processed_images(
    processed_images,
    output_folder
):

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "01_original.jpg"
        ),
        processed_images["original"]
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "02_grayscale.jpg"
        ),
        processed_images["gray"]
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "03_blurred.jpg"
        ),
        processed_images["blurred"]
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "04_clahe_enhanced.jpg"
        ),
        processed_images["enhanced"]
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "05_threshold.jpg"
        ),
        processed_images["threshold"]
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "06_edges.jpg"
        ),
        processed_images["edges"]
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            "07_morphology.jpg"
        ),
        processed_images["morphed"]
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

    processed = preprocess_palm_image(
        image_path
    )

    save_processed_images(
        processed,
        output_folder
    )

    print(
        "Palm image preprocessing completed successfully."
    )

    print(
        "Processed images saved to:"
    )

    print(
        output_folder
    )