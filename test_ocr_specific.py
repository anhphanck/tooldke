
import os
import re
import subprocess
from PIL import Image
from io import BytesIO

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGE_DIR = r"D:\dke\10090-12"

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
    text = result.stdout.decode("utf-8", errors="replace")
    return text

def extract_values(ocr_text):
    values = {
        "Delta_t": None,
        "Maximum": None,
        "Mean": None,
        "RMS": None
    }
    
    callout_idx = ocr_text.lower().find("callout")
    meas1_idx = ocr_text.lower().find("meas 1")
    meas2_idx = ocr_text.lower().find("meas 2")
    meas3_idx = ocr_text.lower().find("meas 3")
    
    if meas1_idx == -1:
        meas1_idx = len(ocr_text)
    if meas2_idx == -1:
        meas2_idx = len(ocr_text)
    if meas3_idx == -1:
        meas3_idx = len(ocr_text)
    
    # -------------------------- DELTA_T --------------------------
    # Priority 1: In Callout section, find t: XXXXX s (must have decimal)
    if callout_idx != -1:
        callout_section = ocr_text[callout_idx:meas1_idx]
        t_pattern = re.compile(r"t[:\s]*(\d+\.\d+)\s*s", re.IGNORECASE)
        t_match = t_pattern.search(callout_section)
        if t_match:
            try:
                val = float(t_match.group(1))
                if val < 100:
                    # Check if this number is not near Aa/At
                    match_start = callout_section.find(t_match.group(1))
                    context = callout_section[max(0, match_start - 30):match_start]
                    if "aa/at" not in context.lower():
                        values["Delta_t"] = val
            except ValueError:
                pass
    # Priority 2: If not, find At: XXXXX (with decimal) at the beginning, skip if near Aa/At
    if values["Delta_t"] is None:
        at_pattern = re.compile(r"At[:\s]*(\d+\.\d+)", re.IGNORECASE)
        at_matches = list(at_pattern.finditer(ocr_text[:1000]))
        for at_match in at_matches:
            try:
                val = float(at_match.group(1))
                if val < 100:
                    # Check if this At is not near Aa/At
                    match_start = at_match.start()
                    context = ocr_text[max(0, match_start - 30):match_start]
                    if "aa/at" not in context.lower():
                        values["Delta_t"] = val
                        break
            except ValueError:
                pass
    
    # -------------------------- MAXIMUM --------------------------
    max_section = ocr_text[meas1_idx:]
    max_pattern = re.compile(r"(?:Maximum|Max).*?(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
    max_matches = max_pattern.findall(max_section)
    for match in max_matches:
        try:
            val = float(match)
            if val > 5:  # Skip measurement index 1,2,3
                values["Maximum"] = val
                break
        except ValueError:
            pass
    
    # -------------------------- MEAN --------------------------
    mean_section = ocr_text[meas2_idx:meas3_idx]
    # Find only numbers with decimal points
    mean_num_pattern = re.compile(r"(\d+\.\d+)")
    mean_num_matches = mean_num_pattern.findall(mean_section)
    for match in mean_num_matches:
        try:
            val = float(match)
            if 0.5 < val < 5:
                values["Mean"] = val
                break
        except ValueError:
            pass
    # If still not found, look for u'... without colon (with decimal)
    if values["Mean"] is None:
        u_pattern = re.compile(r"u['\"]?(\d+\.\d+)", re.IGNORECASE)
        u_match = u_pattern.search(mean_section)
        if u_match:
            try:
                val = float(u_match.group(1))
                if 0.5 < val <5:
                    values["Mean"] = val
            except ValueError:
                pass
    # If still none, look in meas1 section for u'... (the first one is Maximum, second might be Mean?)
    if values["Mean"] is None:
        meas1_section = ocr_text[meas1_idx:meas2_idx]
        u_matches = list(re.finditer(r"u['\"]?(\d+\.\d+)", meas1_section, re.IGNORECASE))
        if len(u_matches) >= 1:
            # Wait no, the first u' in meas1 is Maximum, so check if there's another?
            # Or wait in some images, maybe the Mean is in meas1? No.
            # Let's just skip for now? Or use a default? No, let's see.
            pass
    
    # -------------------------- RMS --------------------------
    rms_section = ocr_text[meas3_idx:]
    rms_pattern = re.compile(r"(?:RMS|rms|RIMS|Hy\s*RIMS).*?(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
    rms_matches = rms_pattern.findall(rms_section)
    for match in rms_matches:
        try:
            val = float(match)
            if 0.5 < val < 5:
                values["RMS"] = val
                break
        except ValueError:
            pass
    # If still not found, look for any decimal in rms_section
    if values["RMS"] is None:
        rms_num_pattern = re.compile(r"(\d+\.\d+)")
        rms_num_matches = rms_num_pattern.findall(rms_section)
        for match in rms_num_matches:
            try:
                val = float(match)
                if 0.5 < val <5:
                    values["RMS"] = val
                    break
            except ValueError:
                pass
    
    return values

# Check all images in directory
image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(".png")]
image_files.sort()

print(f"Checking {len(image_files)} images...\n")
for filename in image_files:
    image_path = os.path.join(IMAGE_DIR, filename)
    ocr_text = ocr_image(image_path)
    values = extract_values(ocr_text)
    print(f"{filename}:")
    print(f"  Values: {values}\n")
