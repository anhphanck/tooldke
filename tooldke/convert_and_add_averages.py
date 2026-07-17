
import os
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.drawing.image import Image

# File paths
img_dir = r'd:\dke3\tooldke\10090-12'
original_excel = r'd:\dke3\tooldke\code\extracted_data_final_v9.xlsx'
template_excel = r'd:\dke3\tooldke\code\extracted_data_final_v9_with_averages.xlsx'
output_excel = r'd:\dke3\tooldke\code\extracted_data_final_v9_with_averages.xlsx'

# Step 1: Process the data sheets first using original file
wb_data = openpyxl.load_workbook(original_excel)
yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
data_sheets = [sheet for sheet in wb_data.sheetnames if sheet != 'img']

for sheet_name in data_sheets:
    ws = wb_data[sheet_name]
    
    # Convert Mean values (column E, index 5) from uA to mA
    for row_idx in range(2, ws.max_row + 1):
        mean_cell = ws.cell(row=row_idx, column=5)
        if mean_cell.value is not None and isinstance(mean_cell.value, (int, float)):
            if mean_cell.value > 10:
                mean_cell.value = mean_cell.value / 1000
    
    # Add average row
    last_row = ws.max_row
    avg_row = last_row + 1
    ws.cell(row=avg_row, column=1, value='Average')
    
    for col in range(1, ws.max_column + 1):
        ws.cell(row=avg_row, column=col).fill = yellow_fill
    
    # Add formulas
    col_d = openpyxl.utils.get_column_letter(4)
    ws.cell(row=avg_row, column=4, value=f'=AVERAGE({col_d}2:{col_d}{last_row})')
    
    col_c = openpyxl.utils.get_column_letter(3)
    ws.cell(row=avg_row, column=5, value=f'=AVERAGE({col_c}2:{col_c}{last_row})')
    
    col_e = openpyxl.utils.get_column_letter(5)
    ws.cell(row=avg_row, column=3, value=f'=AVERAGE({col_e}2:{col_e}{last_row})')

# Step 2: Load the template for img sheet
wb_template = openpyxl.load_workbook(template_excel)
if 'img' in wb_template.sheetnames:
    ws_img = wb_template['img']
else:
    ws_img = wb_template.create_sheet('img')

# Step 3: Group images
image_groups = {
    '0C': [],
    '10C': [],
    '25C': [],
    '40C': []
}
suffix_map = {'T0': '0C', 'T10': '10C', 'T28': '25C', 'T40': '40C'}

for filename in os.listdir(img_dir):
    if filename.endswith('.png'):
        for suffix, group_key in suffix_map.items():
            if f'_{suffix}_' in filename:
                image_groups[group_key].append(os.path.join(img_dir, filename))
                break

# Take first 5 images per group
for key in image_groups:
    image_groups[key] = image_groups[key][:5]

# Step 4: Map sections to their starting rows
section_row_map = {
    '0C': 79,
    '10C': 152,
    '25C': 226,
    '40C': 300
}

# Columns for 1-5 placeholders (C, R, AG, AV, BK)
placeholder_cols = ['C', 'R', 'AG', 'AV', 'BK']

# Insert images into each section
for section_key in ['0C', '10C', '25C', '40C']:
    start_row = section_row_map[section_key]
    images = image_groups[section_key]
    
    for img_idx, img_path in enumerate(images):
        if os.path.exists(img_path) and img_idx < len(placeholder_cols):
            col_letter = placeholder_cols[img_idx]
            img = Image(img_path)
            
            # Resize image to fit the placeholder (adjust size as needed)
            img.width = 600
            img.height = 400
            
            # Insert image at the placeholder column and start_row + 1
            anchor_cell = f'{col_letter}{start_row + 10}'
            ws_img.add_image(img, anchor_cell)

# Step 5: Copy processed data sheets to template workbook
for sheet_name in data_sheets:
    if sheet_name in wb_template.sheetnames:
        del wb_template[sheet_name]
    # Copy the sheet
    ws_data = wb_data[sheet_name]
    ws_new = wb_template.create_sheet(sheet_name)
    
    # Copy cell values and styles
    for row in ws_data.iter_rows():
        for cell in row:
            new_cell = ws_new.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                new_cell.font = cell.font.copy()
                new_cell.border = cell.border.copy()
                new_cell.fill = cell.fill.copy()
                new_cell.number_format = cell.number_format
                new_cell.protection = cell.protection.copy()
                new_cell.alignment = cell.alignment.copy()
    
    # Copy merged cells
    for merged_cell in ws_data.merged_cells.ranges:
        ws_new.merge_cells(str(merged_cell))
    
    # Copy row heights and column widths
    for row_idx, row_dim in ws_data.row_dimensions.items():
        ws_new.row_dimensions[row_idx].height = row_dim.height
    for col_idx, col_dim in ws_data.column_dimensions.items():
        ws_new.column_dimensions[col_idx].width = col_dim.width
    
    # Copy images if any
    for img in ws_data._images:
        ws_new.add_image(img, img.anchor._from.coordinate)

# Step 6: Save the final workbook
wb_template.save(output_excel)
print("Done! Processed data, added averages, and inserted images into img sheet.")
