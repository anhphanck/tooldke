
import pandas as pd

# List of files to check
files = [
    r"D:\dke\tooldke\extracted_data.xlsx",
    r"D:\dke\tooldke\extracted_data_debug.xlsx",
]

for file_path in files:
    print("\n" + "="*80)
    print(f"Reading file: {file_path}")
    print("="*80)
    try:
        xl = pd.ExcelFile(file_path)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(df.to_string())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
