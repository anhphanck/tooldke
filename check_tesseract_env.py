
import pytesseract
import os
from pytesseract import pytesseract as pt

print("Tesseract command:", pt.tesseract_cmd)
print("PATH:", os.environ.get('PATH', ''))
