import os
import sys
sys.path.insert(0, r'd:\dke')
from custom_extract import extract_values_from_image, ocr_region
from PIL import Image

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGE_DIR = r"D:\dke\10090-12"

# Test T32 images
image_files = [f for f in os.listdir(IMAGE_DIR) if "T32" in f]
print(f"Found {len(image_files)} T32 images:")
for filename in image_files:
    print(f"\n--- {filename} ---")
    image_path = os.path.join(IMAGE_DIR, filename)
    img = Image.open(image_path)
    width, height = img.size
    
    delta_t_bbox = (0, 0, 1920, 400)
    delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
    print("Delta_t OCR text:")
    print(repr(delta_t_text))
    
    values = extract_values_from_image(image_path)
    print(f"Extracted values: {values}")
