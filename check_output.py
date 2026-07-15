
import pandas as pd

OUTPUT_FILE = r"D:\dke\code\extracted_data_final_v9.xlsx"

# Read first sheet
xl = pd.ExcelFile(OUTPUT_FILE)
for sheet_name in xl.sheet_names:
    df = pd.read_excel(OUTPUT_FILE, sheet_name=sheet_name)
    print(f"=== Sheet: {sheet_name} ===")
    print(df.head())
    print()
