
import os
import re
import subprocess
from PIL import Image
import pandas as pd
from io import BytesIO
from statistics import mean
from collections import defaultdict

# Configuration
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGE_DIR = r"D:\dke\10090-12"
OUTPUT_FILE = r"D:\dke\code\extracted_data_complete.xlsx"

def ocr_image(image_path):
    """Run OCR on an image using Tesseract via stdin."""
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
    """Extract Delta_t, Maximum, Mean, RMS from OCR text using regex."""
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
    # Priority 1: Look anywhere in ocr_text for t: XXXXX s
    t_pattern = re.compile(r"t[:\s]*(\d+\.\d+)\s*s", re.IGNORECASE)
    t_match = t_pattern.search(ocr_text)
    if t_match:
        try:
            val = float(t_match.group(1))
            if val < 100:
                # Check if this number is not near Aa/At
                match_start = t_match.start()
                context = ocr_text[max(0, match_start - 40):match_start]
                if "aa/at" not in context.lower():
                    values["Delta_t"] = val
        except ValueError:
            pass
    # Priority 2: Look for At: XXXXX anywhere, skip near Aa/At
    if values["Delta_t"] is None:
        at_pattern = re.compile(r"At[:\s]*(\d+\.\d+)", re.IGNORECASE)
        at_matches = list(at_pattern.finditer(ocr_text))
        for at_match in at_matches:
            try:
                val = float(at_match.group(1))
                if val < 100:
                    match_start = at_match.start()
                    context = ocr_text[max(0, match_start - 40):match_start]
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

def parse_filename(filename):
    """Extract case number and sheet name from filename."""
    case_match = re.search(r"case(\d+)", filename)
    sheet_match = re.search(r"_(T\d+)_", filename)
    
    case = int(case_match.group(1)) if case_match else None
    sheet = sheet_match.group(1) if sheet_match else None
    
    return case, sheet

def get_sheet_number(sheet_name):
    """Extract the numeric part from sheet name (e.g., T0 → 0, T2 → 2)"""
    match = re.search(r"T(\d+)", sheet_name)
    if match:
        return int(match.group(1))
    return float('inf')

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(".png")]
    image_files.sort()
    
    if not image_files:
        print("No PNG files found in", IMAGE_DIR)
        return
    
    # First pass: collect all data
    all_data = []
    for filename in image_files:
        print(f"Processing {filename}...")
        image_path = os.path.join(IMAGE_DIR, filename)
        
        try:
            ocr_text = ocr_image(image_path)
            values = extract_values(ocr_text)
            case, sheet = parse_filename(filename)
            all_data.append({
                "Case": case,
                "Sheet": sheet,
                "Filename": filename,
                "Delta_t": values["Delta_t"],
                "Maximum": values["Maximum"],
                "Mean": values["Mean"],
                "RMS": values["RMS"]
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Fill missing values using averages per (case, sheet)
    group_values = defaultdict(lambda: defaultdict(list))
    for data in all_data:
        key = (data["Case"], data["Sheet"])
        if data["Delta_t"] is not None:
            group_values[key]["Delta_t"].append(data["Delta_t"])
        if data["Maximum"] is not None:
            group_values[key]["Maximum"].append(data["Maximum"])
        if data["Mean"] is not None:
            group_values[key]["Mean"].append(data["Mean"])
        if data["RMS"] is not None:
            group_values[key]["RMS"].append(data["RMS"])
    
    # Now fill missing values
    filled_data = []
    for data in all_data:
        key = (data["Case"], data["Sheet"])
        filled = data.copy()
        
        if filled["Delta_t"] is None and len(group_values[key]["Delta_t"]) > 0:
            filled["Delta_t"] = round(mean(group_values[key]["Delta_t"]), 4)
        if filled["Maximum"] is None and len(group_values[key]["Maximum"]) > 0:
            filled["Maximum"] = round(mean(group_values[key]["Maximum"]), 4)
        if filled["Mean"] is None and len(group_values[key]["Mean"]) > 0:
            filled["Mean"] = round(mean(group_values[key]["Mean"]), 4)
        if filled["RMS"] is None and len(group_values[key]["RMS"]) > 0:
            filled["RMS"] = round(mean(group_values[key]["RMS"]), 4)
        
        filled_data.append(filled)
    
    # Organize by sheet
    data_by_sheet = defaultdict(list)
    for data in filled_data:
        sheet = data["Sheet"]
        data_to_write = data.copy()
        del data_to_write["Sheet"]
        data_by_sheet[sheet].append(data_to_write)
    
    # Write to Excel
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        sorted_sheets = sorted(data_by_sheet.keys(), key=get_sheet_number)
        for sheet in sorted_sheets:
            data = data_by_sheet[sheet]
            data_sorted = sorted(data, key=lambda x: x["Case"])
            df = pd.DataFrame(data_sorted)
            df.to_excel(writer, sheet_name=sheet, index=False)
    
    print(f"Done! Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
