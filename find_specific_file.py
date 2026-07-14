
import pandas as pd

xl = pd.ExcelFile(r'D:\dke\code\extracted_data_complete.xlsx')
target_filename = '2026_07_10_13_00_49_11_case01_T0_P0.png'

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    matching = df[df['Filename'] == target_filename]
    if not matching.empty:
        print(f"Found in {sheet}:")
        print(matching[['Case', 'Filename', 'Delta_t', 'Maximum', 'Mean', 'RMS']])
        break
