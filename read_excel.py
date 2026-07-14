
import pandas as pd

for xls_path in [
    r"D:\dke\code\extracted_data_debug.xlsx",
    r"D:\dke\tooldke\extracted_data.xlsx",
    r"D:\dke\tooldke\extracted_data_debug.xlsx",
]:
    print(f"\n{'='*60}")
    print(f"Checking {xls_path}")
    print('='*60)
    try:
        xls = pd.ExcelFile(xls_path)
        print("Sheet names:", xls.sheet_names)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"\n=== Sheet {sheet_name}:")
            print(df.to_string())
    except Exception as e:
        print(f"Error reading {xls_path}: {e}")
