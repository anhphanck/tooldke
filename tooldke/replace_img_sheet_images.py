
import openpyxl
import os
import shutil
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils import get_column_letter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(SCRIPT_DIR, "10090-12")
REFERENCE_FILE = os.path.join(SCRIPT_DIR, "code", "New XLSX 工作表_filled.xlsx")
DATA_FILE = os.path.join(SCRIPT_DIR, "code", "extracted_data_final_v9.xlsx")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "code", "extracted_data_final_v9_with_averages.xlsx")

# Step 1: Make a copy of the reference file as our output file (preserves the img sheet perfectly!)
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
shutil.copy(REFERENCE_FILE, OUTPUT_FILE)

# Step 2: Load both the data file and the new output file
data_wb = openpyxl.load_workbook(DATA_FILE)
output_wb = openpyxl.load_workbook(OUTPUT_FILE)

# Delete extra sheets (Sheet1, Sheet2, Sheet3) from the output file
for sheet_name in ["Sheet1", "Sheet2", "Sheet3"]:
    if sheet_name in output_wb.sheetnames:
        del output_wb[sheet_name]
        print(f"Deleted extra sheet: {sheet_name}")

# Step 3: Copy all data sheets from data_wb to output_wb (skip any "img" sheet in data_wb)
for sheet_name in data_wb.sheetnames:
    if sheet_name == "img":
        continue  # Skip if data file has an img sheet
    data_ws = data_wb[sheet_name]
    
    # Create new sheet in output_wb
    if sheet_name in output_wb.sheetnames:
        del output_wb[sheet_name]  # Delete if sheet already exists
    output_ws = output_wb.create_sheet(title=sheet_name)
    
    # Copy column dimensions
    for col in data_ws.column_dimensions:
        output_ws.column_dimensions[col] = data_ws.column_dimensions[col]
    
    # Copy row dimensions
    for row in data_ws.row_dimensions:
        output_ws.row_dimensions[row] = data_ws.row_dimensions[row]
    
    # Copy cell values and basic styles
    for row in data_ws.iter_rows():
        for cell in row:
            output_cell = output_ws.cell(row=cell.row, column=cell.column)
            output_cell.value = cell.value
            if cell.has_style:
                output_cell.font = cell.font
                output_cell.border = cell.border
                output_cell.fill = cell.fill
                output_cell.number_format = cell.number_format
                output_cell.alignment = cell.alignment
    
    # Copy merged cells
    for merged_cell in data_ws.merged_cells.ranges:
        output_ws.merge_cells(str(merged_cell))

# Step 4: Now process the img sheet: find the correct cells and add images!
# First, find the img sheet in the output file - it's probably the first sheet, named "圖檔上傳  "
img_sheet_name = "圖檔上傳  "
if img_sheet_name not in output_wb.sheetnames:
    # If not, look for any sheet that might be the img sheet
    print(f"Warning: Sheet {img_sheet_name} not found, using first sheet!")
    img_sheet_name = output_wb.sheetnames[0]

img_ws = output_wb[img_sheet_name]

# Rename the img sheet to "img"
if img_sheet_name != "img":
    img_ws.title = "img"
    img_sheet_name = "img"

# Step 5: Find the positions for our images in the img sheet!
# First, find the rows for 0C, 10C, 25C, 40C
temp_rows = {}
for row in img_ws.iter_rows():
    for cell in row:
        cell_val = str(cell.value).strip() if cell.value else ""
        if cell_val in ["0C", "10C", "25C", "40C"]:
            temp_rows[cell_val] = cell.row
            print(f"Found {cell_val} at row {cell.row}")

print(f"Found temp rows: {temp_rows}")

# Now, for each temperature, find cells labeled 1-5 in that row (or the next row)
image_anchors = []  # Will hold cell addresses like "C79" for each image

temps_order = ["0C", "10C", "25C", "40C"]
for temp in temps_order:
    if temp not in temp_rows:
        continue
    temp_row = temp_rows[temp]
    # Check this row and maybe the row after (in case label is in row 1, images in row 2)
    for check_row in [temp_row, temp_row + 1]:
        found_in_this_row = 0
        for col in img_ws.iter_cols(min_row=check_row, max_row=check_row):
            cell = col[0]
            cell_val = str(cell.value).strip() if cell.value else ""
            if cell_val in ["1", "2", "3", "4", "5"]:
                # Let's just use the cell itself as the anchor (not the one to the right)
                anchor_cell = cell.coordinate
                image_anchors.append(anchor_cell)
                found_in_this_row +=1
                print(f"Found label {cell_val} for {temp} at {anchor_cell}, using that as anchor")
        if found_in_this_row ==5:
            break  # Stop checking rows once we have all 5 for this temp

print(f"Total image anchors found: {len(image_anchors)}")

# If we didn't find enough anchors, let's try a fallback approach:
# Look at the reference image the user sent earlier: 0C, then columns 1-5 next to it
if len(image_anchors) < 20:
    print("Not enough anchors found, using fallback approach!")
    image_anchors = []
    temps_order_fallback = ["0C", "10C", "25C", "40C"]
    for temp in temps_order_fallback:
        if temp not in temp_rows:
            continue
        temp_row = temp_rows[temp]
        # Let's assume labels 1-5 are in columns B-F, same row as temp or next row
        for check_row in [temp_row, temp_row +1]:
            for col in ["B", "C", "D", "E", "F"]:
                anchor_cell = f"{col}{check_row}"
                image_anchors.append(anchor_cell)
            if len(image_anchors) >=5*(temps_order_fallback.index(temp)+1):
                break

print(f"Final image anchors ({len(image_anchors)}): {image_anchors}")

# Step 6: Collect the 20 images from IMAGE_DIR
temp_map = {
    "T0": [],
    "T10": [],
    "T28": [],
    "T40": []
}
all_image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(".png")]
all_image_files.sort()
for f in all_image_files:
    if "_T0_" in f:
        temp_map["T0"].append(f)
    elif "_T10_" in f:
        temp_map["T10"].append(f)
    elif "_T28_" in f:
        temp_map["T28"].append(f)
    elif "_T40_" in f:
        temp_map["T40"].append(f)

# Combine them in order: T0, T10, T28, T40, 5 each
all_images = []
for temp in ["T0", "T10", "T28", "T40"]:
    all_images.extend(temp_map[temp][:5])

# Step 7: Add new images using the anchors we found!
added_count = 0
for idx in range(len(all_images)):
    if idx >= len(image_anchors):
        print(f"Not enough anchors, stopping at {idx} images")
        break
    img_path = os.path.join(IMAGE_DIR, all_images[idx])
    if os.path.exists(img_path):
        excel_img = ExcelImage(img_path)
        excel_img.anchor = image_anchors[idx]
        # Set fixed image size
        excel_img.width = 900
        excel_img.height = 600
        img_ws.add_image(excel_img)
        added_count += 1
        print(f"Added image {idx+1}/{len(all_images)}: {all_images[idx]} at {image_anchors[idx]} (size 900x600)")

print(f"Copied data sheets and added {added_count} images in img sheet!")

# Step 8: Now process the data sheets (convert Mean to mA and add averages, right here, so we don't need a separate script!)
from openpyxl.styles import PatternFill

yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

# Process each data sheet (skip img sheet)
for sheet_name in output_wb.sheetnames:
    if sheet_name == "img":
        continue
    ws = output_wb[sheet_name]
    
    # Step 8a: Convert Mean values from uA to mA
    for row_idx in range(2, ws.max_row + 1):
        mean_cell = ws.cell(row=row_idx, column=5)  # Column E is Mean
        if mean_cell.value is not None and isinstance(mean_cell.value, (int, float)):
            if mean_cell.value > 10:  # Assume values >10 are uA
                mean_cell.value = mean_cell.value / 1000
    
    # Step 8b: Add averages row
    last_row = ws.max_row
    avg_row = last_row + 1
    ws.cell(row=avg_row, column=1, value="Average")
    
    # Apply yellow fill
    for col in range(1, ws.max_column + 1):
        ws.cell(row=avg_row, column=col).fill = yellow_fill
    
    # Add AVERAGE formulas (swap column C and E as before)
    col_d_letter = get_column_letter(4)
    ws.cell(row=avg_row, column=4, value=f'=AVERAGE({col_d_letter}2:{col_d_letter}{last_row})')
    
    col_c_letter = get_column_letter(3)
    ws.cell(row=avg_row, column=5, value=f'=AVERAGE({col_c_letter}2:{col_c_letter}{last_row})')
    
    col_e_letter = get_column_letter(5)
    ws.cell(row=avg_row, column=3, value=f'=AVERAGE({col_e_letter}2:{col_e_letter}{last_row})')

# Step 9: Save the output file!
output_wb.save(OUTPUT_FILE)
print("Done! Final file saved!")
