import os
import sys
sys.path.insert(0, r'd:\dke')
from custom_extract import extract_values_from_image, ocr_region
from PIL import Image

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGE_DIR = r"D:\dke\10090-12"

# Check T6, T10, T28
for t_label in ['T6', 'T10', 'T28']:
    print(f"\n=== {t_label} ===")
    t_files = [f for f in os.listdir(IMAGE_DIR) if f"_{t_label}_" in f]
    for filename in t_files:
        print(f"\nFile: {filename}")
        image_path = os.path.join(IMAGE_DIR, filename)
        img = Image.open(image_path)
        delta_t_bbox = (0, 0, 1920, 400)
        delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
        print("Delta_t OCR text:")
        print(repr(delta_t_text))
        values = extract_values_from_image(image_path)
        print(f"Extracted values: {values}")
