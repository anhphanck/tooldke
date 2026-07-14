
import pytesseract
import subprocess
import sys

print("tesseract_cmd:", pytesseract.pytesseract.tesseract_cmd)

# Try running tesseract directly with --version
try:
    result = subprocess.run(
        [pytesseract.pytesseract.tesseract_cmd, "--version"],
        capture_output=True,
        text=True
    )
    print("Tesseract version output:", result.stdout)
    print("Tesseract stderr:", result.stderr)
except Exception as e:
    print("Error running tesseract:", e)
