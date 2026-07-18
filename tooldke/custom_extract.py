import os
import re
import subprocess
import json
from PIL import Image
import pandas as pd
from io import BytesIO
from statistics import mean
from collections import defaultdict
from copy import copy
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as ExcelImage

# Configuration - use relative paths for portability
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Get current directory of the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(SCRIPT_DIR, "10090-12")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "code", "extracted_data_final_v9.xlsx")  
TRACKING_FILE = os.path.join(SCRIPT_DIR, "code", "used_images_tracking.json")

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

def load_tracking_file():
    """Load tracking file that keeps track of used images per temperature"""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    # Default structure if file doesn't exist or is invalid
    return {"0C": [], "10C": [], "25C": [], "40C": []}

def save_tracking_file(tracking_data):
    """Save tracking file"""
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(tracking_data, f, ensure_ascii=False, indent=4)

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

    # Now add the 'img' sheet with 20 images (disabled for now)
    # add_img_sheet(OUTPUT_FILE, IMAGE_DIR)

    print(f"Done! Data saved to {OUTPUT_FILE}")

def add_img_sheet(excel_path, image_dir):
    """Add 'img' sheet after T40 with 20 images arranged in grid, tracking used images, using reference file's structure"""
    print("Adding img sheet...")
    wb = load_workbook(excel_path)
    
    # Load reference file
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    REFERENCE_FILE = os.path.join(SCRIPT_DIR, "code", "New XLSX 工作表_filled.xlsx")
    ref_wb = load_workbook(REFERENCE_FILE)
    ref_sheet_name = "圖檔上傳  "
    
    if ref_sheet_name not in ref_wb.sheetnames:
        print(f"Warning: Reference sheet '{ref_sheet_name}' not found! Using default structure...")
        ref_info = None
    else:
        ref_ws = ref_wb[ref_sheet_name]
        ref_info = {
            "images": []
        }
        for img in ref_ws._images:
            ref_info["images"].append({
                "anchor": img.anchor,
                "width": img.width,
                "height": img.height
            })
        print(f"  Loaded {len(ref_info['images'])} reference image positions/sizes")

    # Define temperature to sheet mapping
    temp_map = {
        "0C": "T0",
        "10C": "T10",
        "25C": "T28",
        "40C": "T40"
    }

    # Load tracking data
    tracking = load_tracking_file()

    # Collect images for each temperature (5 each), using new ones each time
    temp_images = {}
    all_image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(".png")]
    all_image_files.sort()

    for temp, sheet_name in temp_map.items():
        # Get all images for this sheet that haven't been used yet
        all_matching_images = []
        for f in all_image_files:
            if f"_{sheet_name}_" in f:
                all_matching_images.append(f)
        
        # Filter out used images
        used_images = set(tracking.get(temp, []))
        available_images = [f for f in all_matching_images if f not in used_images]
        
        # If we don't have enough new images, start over from the beginning
        if len(available_images) < 5:
            print(f"  Not enough new images for {temp}, resetting used images...")
            tracking[temp] = []
            available_images = all_matching_images
        
        # Take the next 5 images
        selected_images = available_images[:5]
        temp_images[temp] = selected_images
        # Mark them as used
        tracking[temp].extend(selected_images)
        print(f"  {temp}: selected {len(selected_images)} new images")

    # Save updated tracking
    save_tracking_file(tracking)

    # Create 'img' sheet by copying reference sheet (if available)
    if "img" in wb.sheetnames:
        del wb["img"]

    # Insert 'img' sheet after T40
    t40_index = None
    for i, sheet_name in enumerate(wb.sheetnames):
        if sheet_name == "T40":
            t40_index = i
            break

    print(f"  Inserting img sheet at index: {t40_index + 1 if t40_index is not None else len(wb.sheetnames)}")
    
    if ref_sheet_name in ref_wb.sheetnames:
        # Copy reference sheet
        ref_ws = ref_wb[ref_sheet_name]
        img_sheet = wb.create_sheet(title="img", index=t40_index + 1 if t40_index is not None else len(wb.sheetnames))
        
        # Copy column dimensions
        for col in ref_ws.column_dimensions:
            img_sheet.column_dimensions[col] = copy(ref_ws.column_dimensions[col])
        
        # Copy row dimensions
        for row in ref_ws.row_dimensions:
            img_sheet.row_dimensions[row] = copy(ref_ws.row_dimensions[row])
        
        # Copy cell values and styles (copy individual attributes)
        for row in ref_ws.iter_rows():
            for cell in row:
                img_cell = img_sheet.cell(row=cell.row, column=cell.column)
                img_cell.value = cell.value
                if cell.has_style:
                    img_cell.font = copy(cell.font)
                    img_cell.border = copy(cell.border)
                    img_cell.fill = copy(cell.fill)
                    img_cell.number_format = cell.number_format
                    img_cell.protection = copy(cell.protection)
                    img_cell.alignment = copy(cell.alignment)
        
        # Copy merged cells
        for merged_cell in ref_ws.merged_cells.ranges:
            img_sheet.merge_cells(str(merged_cell))
    else:
        # Fallback to default structure
        img_sheet = wb.create_sheet(title="img", index=t40_index + 1 if t40_index is not None else len(wb.sheetnames))

    # Combine all images in order: T0, T10, T28, T40
    temps = list(temp_map.keys())
    all_images = []
    for temp in temps:
        all_images.extend(temp_images[temp])
    
    # Add images using reference positions/sizes (if available)
    total_images_added = 0
    for idx, img_file in enumerate(all_images):
        img_path = os.path.join(image_dir, img_file)
        if os.path.exists(img_path):
            excel_img = ExcelImage(img_path)
            
            if ref_info and len(ref_info["images"]) > idx:
                ref_img = ref_info["images"][idx]
                excel_img.width = ref_img["width"]
                excel_img.height = ref_img["height"]
                excel_img.anchor = ref_img["anchor"]
            else:
                # Fallback: arrange images: 4 rows (temperatures) × 5 columns
                img_width = 300  # pixels (make them bigger to see clearly)
                img_height = 200  # pixels
                row_height = 150
                col_width = 40

                # Set row heights and column widths
                for row in range(1, 5):
                    img_sheet.row_dimensions[row].height = row_height
                for col in range(1, 7):  # Columns A-F
                    img_sheet.column_dimensions[chr(64 + col)].width = col_width
                
                # Add temperature label in first column (A)
                temp_idx = idx // 5
                col_idx_in_temp = idx % 5 + 1
                row_idx_in_temp = temp_idx + 1
                if col_idx_in_temp == 1:
                    temp = temps[temp_idx]
                    img_sheet.cell(row=row_idx_in_temp, column=1, value=temp)
                    img_sheet.cell(row=row_idx_in_temp, column=1).font = copy(img_sheet.cell(row=row_idx_in_temp, column=1).font)
                    img_sheet.cell(row=row_idx_in_temp, column=1).font.bold = True
                    img_sheet.cell(row=row_idx_in_temp, column=1).font.size = 14
                
                excel_img.width = img_width
                excel_img.height = img_height
                cell_anchor = f"{chr(64 + col_idx_in_temp + 1)}{row_idx_in_temp}"
                excel_img.anchor = cell_anchor
            
            img_sheet.add_image(excel_img)
            total_images_added += 1

    print(f"  Added {total_images_added} images to img sheet")
    # Save the workbook
    wb.save(excel_path)
    print("  Saved workbook with img sheet!")

if __name__ == "__main__":
    main()
