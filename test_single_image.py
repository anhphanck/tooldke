
import os
import re
import subprocess
from PIL import Image
from io import BytesIO

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_image(image_path):
    img = Image.open(image_path)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    result = subprocess.run(
        [TESSERACT_PATH, "stdin", "stdout"],
        input=buf.read(),
        capture_output=True
    )
    return result.stdout.decode("utf-8", errors="replace")

image_path = r"D:\dke\10090-12\2026_07_09_10_11_36_11_case01_T0_P0.png"
print("=== OCR TEXT ===")
ocr_text = ocr_image(image_path)
print(repr(ocr_text))
