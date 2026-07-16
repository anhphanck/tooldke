import os
import re
import pytesseract
from PIL import Image
import pandas as pd
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as xlImage
from io import BytesIO

# Set Tesseract path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Get project root directory (where this script is located)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
IMAGE_DIR = os.path.join(PROJECT_ROOT, "10090-12")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "code", "extracted_data_final_v9.xlsx")

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Temperature to sheet mapping
TEMP_SHEET_MAP = {
    "T0": "0C",
    "T10": "10C",
    "T28": "25C",  # T28 maps to 25C
    "T40": "40C"
}

def parse_t_number(filename):
    """Extract T number from filename (e.g., T0, T10, T28, T40)"""
    match = re.search(r'(T\d+)', filename)
    return match.group(1) if match else None

def group_images_by_temp(image_files):
    """Group images by temperature using TEMP_SHEET_MAP"""
    groups = {"0C": [], "10C": [], "25C": [], "40C": []}
    for f in image_files:
        t_num = parse_t_number(f)
        if t_num in TEMP_SHEET_MAP:
            sheet = TEMP_SHEET_MAP[t_num]
            groups[sheet].append(f)
    return groups

def get_sheet_number(sheet_name):
    """Helper to sort sheets by temperature order"""
    if not sheet_name:
        return 999
    temp_order = ["0C", "10C", "25C", "40C"]
    if sheet_name in temp_order:
        return temp_order.index(sheet_name)
    return 999

def extract_delta_t(image_path):
    """Extract Delta_t value from image"""
    try:
        pil_img = Image.open(image_path)
        width, height = pil_img.size
        # Crop to Delta_t region
        delta_t_crop = pil_img.crop((width * 0.1, height * 0.38, width * 0.22, height * 0.43))
        delta_t_text = pytesseract.image_to_string(delta_t_crop, config='--psm 7 -c tessedit_char_whitelist=0123456789.')
        delta_t_match = re.search(r'(\d+\.?\d*)', delta_t_text)
        delta_t = float(delta_t_match.group(1)) if delta_t_match else None
        return delta_t
    except Exception as e:
        print(f"Error extracting Delta_t from {os.path.basename(image_path)}: {e}")
        return None

def extract_meas_values(image_path):
    """Extract Maximum, Mean, RMS values from image"""
    try:
        pil_img = Image.open(image_path)
        width, height = pil_img.size
        # Crop to measurement region
        meas_crop = pil_img.crop((width * 0.33, height * 0.72, width * 0.7, height * 0.87))
        meas_text_1 = pytesseract.image_to_string(meas_crop, config='--psm 6')
        meas_text_2 = pytesseract.image_to_string(meas_crop, config='--psm 3')
        
        def find_number(keyword, text1, text2):
            # First try with mA suffix (more accurate)
            pattern_mA = re.compile(rf'{keyword}[\s:]*(\d+\.?\d*)\s*mA', re.IGNORECASE | re.DOTALL)
            match_mA = pattern_mA.search(text1) or pattern_mA.search(text2)
            if match_mA:
                return float(match_mA.group(1))
            # Fallback: try without mA
            pattern = re.compile(rf'{keyword}[\s:]*(\d+\.?\d*)', re.IGNORECASE | re.DOTALL)
            match = pattern.search(text1) or pattern.search(text2)
            return float(match.group(1)) if match else None
        
        maximum = find_number('Maximum', meas_text_1, meas_text_2)
        mean = find_number('Mean', meas_text_1, meas_text_2)
        rms = find_number('RMS', meas_text_1, meas_text_2)
        return maximum, mean, rms
    except Exception as e:
        print(f"Error extracting measurements from {os.path.basename(image_path)}: {e}")
        return None, None, None

def main():
    # Get all PNG files in IMAGE_DIR, filter only case files
    all_files = os.listdir(IMAGE_DIR)
    image_files = [f for f in all_files if f.lower().endswith('.png') and 'case' in f.lower()]
    
    if not image_files:
        print(f"No PNG files found in {IMAGE_DIR}")
        return
    
    data_by_sheet = {}
    
    # Process each image file
    for filename in image_files:
        print(f"Processing {filename}...")
        image_path = os.path.join(IMAGE_DIR, filename)
        
        # Extract Case number
        case_match = re.search(r'case(\d+)', filename, re.IGNORECASE)
        case_num = int(case_match.group(1)) if case_match else None
        
        # Extract sheet name
        t_num = parse_t_number(filename)
        sheet_name = TEMP_SHEET_MAP.get(t_num)
        
        if not sheet_name or case_num is None:
            print(f"Skipping {filename}: missing case or temp info")
            continue
        
        # Extract values
        delta_t = extract_delta_t(image_path)
        maximum, mean, rms = extract_meas_values(image_path)
        
        # Store data
        if sheet_name not in data_by_sheet:
            data_by_sheet[sheet_name] = []
        data_by_sheet[sheet_name].append({
            "Case": case_num,
            "Filename": filename,
            "Delta_t": delta_t,
            "Maximum": maximum,
            "Mean": mean,
            "RMS": rms
        })
    
    try:
        # Write to Excel, only if we have data
        if data_by_sheet:
            with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
                sorted_sheets = sorted(data_by_sheet.keys(), key=get_sheet_number)
                for sheet in sorted_sheets:
                    data = data_by_sheet[sheet]
                    data_sorted = sorted(data, key=lambda x: x["Case"])
                    df = pd.DataFrame(data_sorted)
                    df.to_excel(writer, sheet_name=sheet, index=False)

        # Now add the img sheet with images
        print("Adding img sheet with images...")
        # First, check if OUTPUT_FILE exists (if we wrote data sheets)
        if os.path.exists(OUTPUT_FILE):
            wb = load_workbook(OUTPUT_FILE)
            # Remove old img sheet if exists
            if "img" in wb.sheetnames:
                del wb["img"]
        else:
            # Create a new workbook if no data was written
            from openpyxl import Workbook
            wb = Workbook()
            # Remove the default sheet
            if "Sheet" in wb.sheetnames:
                del wb["Sheet"]
                
        img_sheet = wb.create_sheet(title="img", index=len(wb.sheetnames))  # Add at the end

        # Group images by temperature
        temp_groups = group_images_by_temp(image_files)

        # Layout: 4 rows (0C, 10C, 25C, 40C), 5 columns each
        temps_order = ["0C", "10C", "25C", "40C"]
        row_height = 600  # Excel row height units (taller for bigger images)
        col_width_label = 15  # Column A width for temperature labels
        col_width_image = 90  # Columns B-F width for images

        # Set row heights and column widths
        for row_idx in range(1, 5):
            img_sheet.row_dimensions[row_idx].height = row_height
        img_sheet.column_dimensions["A"].width = col_width_label
        for col_idx in range(2, 7):  # Columns B-F (indices 2-6)
            img_sheet.column_dimensions[chr(64 + col_idx)].width = col_width_image

        # Add images to the sheet
        for temp_row, temp in enumerate(temps_order, 1):
            # Add temperature label in column A
            label_cell = img_sheet.cell(row=temp_row, column=1)
            label_cell.value = temp
            # Make the label bold and bigger
            from openpyxl.styles import Font
            label_cell.font = Font(bold=True, size=14)
            
            images = temp_groups.get(temp, [])
            print(f"Temp {temp} has {len(images)} images")
            # Take first 5 images (or as many as available)
            for col_idx, filename in enumerate(images[:5], 2):  # Start at column 2 (B)
                try:
                    image_path = os.path.join(IMAGE_DIR, filename)
                    # Resize with even larger target size to keep maximum clarity
                    pil_img = Image.open(image_path)
                    original_width, original_height = pil_img.size
                    target_width = 1000  # Larger target width
                    target_height = 550  # Larger target height
                    ratio = min(target_width / original_width, target_height / original_height)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    # Use LANCZOS for high quality downsampling
                    pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save to BytesIO with high quality
                    img_buffer = BytesIO()
                    pil_img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)

                    # Create Excel image
                    xl_img = xlImage(img_buffer)
                    # Position image at cell (temp_row, col_idx)
                    cell = img_sheet.cell(row=temp_row, column=col_idx)
                    xl_img.anchor = cell.coordinate
                    img_sheet.add_image(xl_img)

                except Exception as e:
                    print(f"Error adding image {filename} to img sheet: {e}")

        # Save workbook
        wb.save(OUTPUT_FILE)
        print(f"Done! Data and images saved to {OUTPUT_FILE}")

    except PermissionError:
        print("\n========================================")
        print("LOI: File Excel dang duoc MO!")
        print("Vui long DONG file Excel/WPS truoc khi chay lai!")
        print("========================================\n")
        input("Nhan Enter de thoat...")
        exit(1)
    except Exception as e:
        print(f"\nCo loi xay ra: {e}")
        print("\n========================================")
        print("Vui long kiem tra lai!")
        print("========================================\n")
        input("Nhan Enter de thoat...")
        exit(1)

if __name__ == "__main__":
    main()
