import os
import sys
sys.path.insert(0, r'd:\dke')
from custom_extract import extract_values_from_image

IMAGE_DIR = r"D:\dke\10090-12"

# Test T40 images
image_files = [f for f in os.listdir(IMAGE_DIR) if "T40" in f]
print(f"Found {len(image_files)} T40 images:")
for filename in image_files:
    print(f"\n--- {filename} ---")
    image_path = os.path.join(IMAGE_DIR, filename)
    values = extract_values_from_image(image_path)
    print(f"Extracted values: {values}")

