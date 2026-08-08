import cv2
import os


def load_and_convert_to_gray(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not load image")

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return image, gray