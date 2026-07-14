import os
import sys
sys.path.insert(0, r'd:\dke')
from custom_extract import extract_values_from_image, ocr_region
from PIL import Image

IMAGE_DIR = r"D:\dke\10090-12"
filename = "2026_07_09_10_16_24_11_case04_T6_P0.png"
image_path = os.path.join(IMAGE_DIR, filename)
img = Image.open(image_path)
delta_t_bbox = (0, 0, 1920, 400)
delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
print("Delta_t OCR text lines:")
for i, line in enumerate(delta_t_text.splitlines()):
    print(f"Line {i}: {repr(line.strip())}")
values = extract_values_from_image(image_path)
print(f"\nExtracted values: {values}")
