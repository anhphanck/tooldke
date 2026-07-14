
from PIL import Image
import pytesseract
import tempfile
import os

# Test with one of the images
image_path = r"D:\dke\10090-12\2026_07_11_09_10_05_11_case01_T0_P0.png"
img = Image.open(image_path)
print(f"Image size: {img.size}")

# Save to a simple temp file with ASCII name
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    tmp_path = tmp.name
    img.save(tmp_path)

try:
    # Now pass the file path to pytesseract
    text = pytesseract.image_to_string(tmp_path)
    print("OCR text:", repr(text))
finally:
    # Clean up the temp file
    os.unlink(tmp_path)
