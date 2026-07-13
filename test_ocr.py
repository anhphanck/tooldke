
import os
import re
import sys
from PIL import Image
import pytesseract

# Configure Tesseract path (if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_region(img, bbox, config='--psm 6'):
    cropped = img.crop(bbox)
    # Preprocess image: just convert to grayscale
    gray = cropped.convert('L')
    text = pytesseract.image_to_string(gray, config=config)
    return text.strip()

def test_image(image_path):
    print("Testing file:", image_path)
    print()
    
    # Open image
    img = Image.open(image_path)
    width, height = img.size
    print("Image size: width=", width, ", height=", height)
    print()
    
    # ---------- ADJUST THESE BBOX VALUES HERE ----------
    # For 1920x1080 images - expanded to cover more area
    delta_t_bbox = (400, 20, 1500, 220)
    meas_bbox = (1500, 120, 1920, 650)
    # ---------------------------------------------------
    
    # Perform OCR
    delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
    meas_text = ocr_region(img, meas_bbox, config='--psm 6')
    
    print("=== Text from delta_t region ===")
    print(repr(delta_t_text))  # Use repr to see whitespace and special characters
    print()
    print("=== Text from Meas region ===")
    print(repr(meas_text))
    print()
    
    # Parse values
    full_text = delta_t_text + "\n" + meas_text
    
    def clean_number(s):
        s = s.replace(',', '.').strip('.')
        return float(s)
    
    # Find Delta_t - look for any number with 's' in delta_t_text
    delta_t_match = re.search(r'([\d.,]+)\s*s', delta_t_text, re.IGNORECASE)
    max_match = re.search(r'Maximum[^\d]*([\d.,]+)', meas_text, re.IGNORECASE)
    mean_match = re.search(r'Mean[^\d]*([\d.,]+)', meas_text, re.IGNORECASE)
    rms_match = re.search(r'RMS[^\d]*([\d.,]+)', meas_text, re.IGNORECASE)
    
    print("=== Parsed results ===")
    if delta_t_match:
        print("Delta_t:", clean_number(delta_t_match.group(1)))
    else:
        print("Delta_t: NOT FOUND!")
    if max_match:
        print("Maximum:", clean_number(max_match.group(1)))
    if mean_match:
        print("Mean:", clean_number(mean_match.group(1)))
    if rms_match:
        print("RMS:", clean_number(rms_match.group(1)))

if __name__ == "__main__":
    input_dir = r'D:\dke\10090-12'
    # If a filename is provided as an argument, use it; otherwise use first file
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        image_path = os.path.join(input_dir, filename)
    else:
        files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
        if not files:
            print("No PNG files found!")
            sys.exit(1)
        image_path = os.path.join(input_dir, files[0])
    
    test_image(image_path)
