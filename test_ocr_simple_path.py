
from PIL import Image
import pytesseract
import os

# Test with one of the images
image_path = r"D:\dke\10090-12\2026_07_11_09_10_05_11_case01_T0_P0.png"
img = Image.open(image_path)
print(f"Image size: {img.size}")

# Save to a simple path
simple_path = r"D:\dke\tmp_test.png"
img.save(simple_path)

try:
    # Now pass the file path to pytesseract
    text = pytesseract.image_to_string(simple_path)
    print("OCR text:", repr(text))
finally:
    # Clean up
    if os.path.exists(simple_path):
        os.unlink(simple_path)
