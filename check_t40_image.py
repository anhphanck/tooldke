
from PIL import Image
import subprocess
from io import BytesIO

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGE_DIR = r"D:\dke\10090-12"

# Check a T40 image
img_path = rf"{IMAGE_DIR}\2026_07_10_13_12_19_11_case13_T40_P0.png"
img = Image.open(img_path)
buf = BytesIO()
img.save(buf, format="PNG")
buf.seek(0)

result = subprocess.run([TESSERACT_PATH, "stdin", "stdout"], input=buf.read(), capture_output=True)
print("OCR Text:")
print(result.stdout.decode("utf-8", errors="replace"))
