
import os
import re
import subprocess
from PIL import Image
from io import BytesIO

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGE_PATH = r"D:\dke\10090-12\2026_07_14_18_26_49_11_case01_T0_P0.png"

def ocr_region(img, bbox, config='--psm 6'):
    cropped = img.crop(bbox)
    gray = cropped.convert('L')
    buf = BytesIO()
    gray.save(buf, format='PNG')
    buf.seek(0)
    
    result = subprocess.run(
        [TESSERACT_PATH, "stdin", "stdout", *config.split()],
        input=buf.read(),
        capture_output=True
    )
    return result.stdout.decode('utf-8', errors='replace').strip()

img = Image.open(IMAGE_PATH)
width, height = img.size

delta_t_bbox = (0, 0, 1920, 400)
meas_bbox = (1500, 120, 1920, 650)

delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
meas_text = ocr_region(img, meas_bbox, config='--psm 6')

print("=== Delta_t region OCR ===")
print(delta_t_text)
print("\n=== Meas region OCR ===")
print(meas_text)
