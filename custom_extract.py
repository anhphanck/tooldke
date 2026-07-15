
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
OUTPUT_FILE = r"D:\dke\code\extracted_data_final_v9.xlsx"

def ocr_region(img, bbox, config='--psm 6'):
    """Run OCR on a specific region of the image via stdin to Tesseract"""
    cropped = img.crop(bbox)
    gray = cropped.convert('L')
    buf = BytesIO()
    gray.save(buf, format='PNG')
    buf.seek(0)
    
    result = subprocess.run(
        [TESSERACT_PATH, "stdin", "stdout", *config.split()],
        input=buf.read(),
        capture_output=True
    )
    return result.stdout.decode('utf-8', errors='replace').strip()

def clean_number(s):
    """Clean number string (replace comma with dot, strip extra dots) and round to 3 decimal places"""
    try:
        s = s.replace(',', '.').strip('.')
        if not s:  # Skip empty strings
            return None
        num = float(s)
        return round(num, 3)
    except ValueError:
        return None

def extract_values_from_image(image_path):
    """Extract Delta_t, Maximum, Mean, RMS from image using region-based OCR"""
    values = {
        "Delta_t": None,
        "Maximum": None,
        "Mean": None,
        "RMS": None
    }
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Bounding boxes - expanded delta_t region
        delta_t_bbox = (0, 0, 1920, 400)  # Larger area for delta_t
        meas_bbox = (1500, 120, 1920, 650)
        
        # OCR on regions
        delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
        meas_text = ocr_region(img, meas_bbox, config='--psm 6')
        
        # Extract Delta_t - FIRST prioritize "At:" or "Δt:" (delta t), but NOT in "Aa/At", "1/At", "W/At", etc.
        # Also avoid "WAt:" which is the frequency
        import re
        # Split into lines first to make it easier
        lines = delta_t_text.splitlines()
        for line in lines:
            line = line.strip()
            # Skip any line with "Aa/At", "1/At", "W/At", "At:", followed by "mHz" or "Hz"
            if any(x in line.lower() for x in ['aa/at', '1/at', 'w/at', '(', 'wat:', '/at']):
                continue
            # Look for "At:" or "Δt:" in this line - capture up to 3 decimals
            match = re.search(r'(?:[Δ∆]t|At)[:\s]*[^\d]*(\d+(?:[.,]\d{1,3})?)', line, re.IGNORECASE)
            if match:
                num_str = match.group(1)
                num = clean_number(num_str)
                if num is not None and num > 1:
                    # Also check that this line doesn't have "mHz" or "Hz"
                    if 'mhz' not in line.lower() and 'hz' not in line.lower():
                        values['Delta_t'] = num
                        break
        if not values['Delta_t']:
            # Then prioritize values near standalone "t:" or "t " - capture up to 3 decimals
            for t_match in re.finditer(r'\bt[:\s]+[^\d]*(\d+(?:[.,]\d{1,3})?)', delta_t_text, re.IGNORECASE):
                num_str = t_match.group(1)
                num = clean_number(num_str)
                if num is not None and num > 0:  # Skip negative numbers
                    match_start, match_end = t_match.span()
                    # Check before for "at"
                    context_before = delta_t_text[max(0, match_start - 15):match_start].lower()
                    # Check if right after the number there's an "s"
                    right_after = delta_t_text[match_end:match_end + 5].lower().strip()
                    # Check right after for "ms", "hz", "mhz"
                    context_after = delta_t_text[match_end:match_end + 15].lower()
                    if (
                        'at' not in context_before and
                        (right_after.startswith('s') or ('ms' not in context_after and 'hz' not in context_after and 'mhz' not in context_after))
                    ):
                        values['Delta_t'] = num
                        break
        if not values['Delta_t']:
            # Fallback to other s values, skip near bad words - capture up to 3 decimals
            for match in re.finditer(r'(\d+(?:[.,]\d{1,3})?)\s*s', delta_t_text, re.IGNORECASE):
                num_str = match.group(1)
                match_start, match_end = match.span()
                context_before = delta_t_text[max(0, match_start - 20):match_start].lower()
                context_after = delta_t_text[match_end:match_end + 20].lower()
                if (
                    'at' not in context_before and
                    'ms' not in context_after and
                    'hz' not in context_after and
                    'mhz' not in context_after
                ):
                    num = clean_number(num_str)
                    if num is not None and num > 0:
                        values['Delta_t'] = num
                        break
        # If still not found, try numbers in reasonable range - capture up to 3 decimals
        if not values['Delta_t']:
            for match in re.finditer(r'(\d+(?:[.,]\d{1,3})?)', delta_t_text):
                num_str = match.group(1)
                num = clean_number(num_str)
                if num is not None and 1 < num < 1000:
                    match_start, match_end = match.span()
                    context_before = delta_t_text[max(0, match_start - 20):match_start].lower()
                    context_after = delta_t_text[match_end:match_end + 20].lower()
                    if (
                        '#' not in context_before + context_after and
                        'ms' not in context_after and
                        'hz' not in context_after and
                        'mhz' not in context_after and
                        'at' not in context_before
                    ):
                        if '.' in num_str or ',' in num_str:
                            values['Delta_t'] = num
                            break
            if not values['Delta_t']:
                for match in re.finditer(r'(\d+(?:[.,]\d{1,3})?)', delta_t_text):
                    num_str = match.group(1)
                    num = clean_number(num_str)
                    if num is not None and 1 < num < 1000:
                        match_start, match_end = match.span()
                        context_before = delta_t_text[max(0, match_start - 20):match_start].lower()
                        context_after = delta_t_text[match_end:match_end + 20].lower()
                        if (
                            '#' not in context_before + context_after and
                            'ms' not in context_after and
                            'hz' not in context_after and
                            'mhz' not in context_after and
                            'at' not in context_before
                        ):
                            values['Delta_t'] = num
                            break
        
        # Extract Maximum, Mean, RMS - capture up to 3 decimals
        max_match = re.search(r'Maximum[^\d]*(\d+(?:[.,]\d{1,3})?)', meas_text, re.IGNORECASE)
        if max_match:
            num = clean_number(max_match.group(1))
            if num is not None:
                values['Maximum'] = num
        
        mean_match = re.search(r'Mean[^\d]*(\d+(?:[.,]\d{1,3})?)', meas_text, re.IGNORECASE)
        if mean_match:
            num = clean_number(mean_match.group(1))
            if num is not None:
                values['Mean'] = num
        
        rms_match = re.search(r'RMS[^\d]*(\d+(?:[.,]\d{1,3})?)', meas_text, re.IGNORECASE)
        if rms_match:
            num = clean_number(rms_match.group(1))
            if num is not None:
                values['RMS'] = num
    
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    
    return values

def parse_filename(filename):
    """Extract case number and sheet name from filename"""
    case_match = re.search(r"case(\d+)", filename)
    sheet_match = re.search(r"_(T\d+)_", filename)
    
    case = int(case_match.group(1)) if case_match else None
    sheet = sheet_match.group(1) if sheet_match else None
    
    return case, sheet

def get_sheet_number(sheet_name):
    """Extract numeric part from sheet name (e.g., T0 → 0)"""
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
            values = extract_values_from_image(image_path)
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
            filled["Delta_t"] = round(mean(group_values[key]["Delta_t"]), 3)
        if filled["Maximum"] is None and len(group_values[key]["Maximum"]) > 0:
            filled["Maximum"] = round(mean(group_values[key]["Maximum"]), 3)
        if filled["Mean"] is None and len(group_values[key]["Mean"]) > 0:
            filled["Mean"] = round(mean(group_values[key]["Mean"]), 3)
        if filled["RMS"] is None and len(group_values[key]["RMS"]) > 0:
            filled["RMS"] = round(mean(group_values[key]["RMS"]), 3)
        
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
