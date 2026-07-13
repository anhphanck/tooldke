
import os
import re
import sys
import easyocr
from PIL import Image

reader = easyocr.Reader(['en'])

def test_image(image_path):
    print("Testing file:", image_path)
    print()
    
    img = Image.open(image_path)
    width, height = img.size
    print("Image size:", width, "x", height)
    print()
    
    delta_t_bbox = (300, 10, 1600, 250)
    meas_bbox = (1450, 100, 1920, 700)
    
    def ocr_region(bbox):
        left, top, right, bottom = bbox
        cropped = img.crop((left, top, right, bottom))
        results = reader.readtext(cropped, detail=0)
        return ' '.join(results)
    
    delta_t_text = ocr_region(delta_t_bbox)
    meas_text = ocr_region(meas_bbox)
    full_text = delta_t_text + ' ' + meas_text
    
    print("=== Delta_t region text ===")
    print(repr(delta_t_text))
    print()
    print("=== Meas region text ===")
    print(repr(meas_text))
    print()
    
    def clean_number(s):
        s = s.replace(',', '.').strip('.')
        return float(s)
    
    delta_t_match = re.search(r'([\d.,]+)\s*s', delta_t_text, re.IGNORECASE)
    if not delta_t_match:
        numbers = re.findall(r'[\d.,]+', delta_t_text)
        for num_str in numbers:
            try:
                num = clean_number(num_str)
                if 10 < num < 1000:
                    print("Delta_t (fallback):", num)
                    break
            except:
                pass
    else:
        print("Delta_t:", clean_number(delta_t_match.group(1)))
    
    max_match = re.search(r'Maximum[^\d]*([\d.,]+)', full_text, re.IGNORECASE)
    if max_match:
        print("Maximum:", clean_number(max_match.group(1)))
    
    mean_match = re.search(r'Mean[^\d]*([\d.,]+)', full_text, re.IGNORECASE)
    if mean_match:
        print("Mean:", clean_number(mean_match.group(1)))
    
    rms_match = re.search(r'RMS[^\d]*([\d.,]+)', full_text, re.IGNORECASE)
    if rms_match:
        print("RMS:", clean_number(rms_match.group(1)))

if __name__ == "__main__":
    input_dir = r'D:\dke\10090-12'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        image_path = os.path.join(input_dir, filename)
    else:
        files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
        if not files:
            print("No files found")
            sys.exit(1)
        image_path = os.path.join(input_dir, files[0])
    test_image(image_path)
