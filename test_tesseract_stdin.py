
from PIL import Image
import subprocess
import io

# Load the image
img_path = r"D:\dke\10090-12\2026_07_11_09_10_05_11_case01_T0_P0.png"
img = Image.open(img_path)

# Save image to a bytes buffer
buf = io.BytesIO()
img.save(buf, format='PNG')
buf.seek(0)

# Run Tesseract with stdin
tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
result = subprocess.run(
    [tesseract_cmd, "stdin", "stdout"],
    input=buf.read(),
    capture_output=True
)

print("Output:", result.stdout.decode('utf-8', errors='replace'))
print("Errors:", result.stderr.decode('utf-8', errors='replace'))
