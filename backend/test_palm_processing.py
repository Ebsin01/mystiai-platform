from app.services.palm_image_processing import (
    load_and_convert_to_gray
)


image_path = "path/to/your/palm/image.jpg"

image, gray = load_and_convert_to_gray(
    image_path
)

print("Original image shape:", image.shape)
print("Gray image shape:", gray.shape)