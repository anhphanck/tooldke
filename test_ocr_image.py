
from PIL import Image
import pytesseract
import os

# Test with one of the images
image_path = r"D:\dke\10090-12\2026_07_11_09_10_05_11_case01_T0_P0.png"
img = Image.open(image_path)
print(f"Image size: {img.size}")

# Let's try to run OCR on the whole image
text = pytesseract.image_to_string(img)
print("OCR text:", repr(text))
