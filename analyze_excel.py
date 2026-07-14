
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\tooldke\extracted_data_debug.xlsx")
for sheet_name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet_name)
    print(f"=== Sheet: {sheet_name} ===")
    print(df.head())
    print("\nColumns:", df.columns.tolist())
    print()
