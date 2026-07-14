import os
import sys
sys.path.insert(0, r'd:\dke')
from custom_extract import extract_values_from_image, ocr_region
from PIL import Image

IMAGE_DIR = r"D:\dke\10090-12"
filename = "2026_07_09_10_11_36_11_case01_T0_P0.png"
image_path = os.path.join(IMAGE_DIR, filename)
img = Image.open(image_path)
delta_t_bbox = (0, 0, 1920, 400)
delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
print(f"File: {filename}")
print("Delta_t OCR text:")
print(repr(delta_t_text))
values = extract_values_from_image(image_path)
print(f"Extracted values: {values}")
