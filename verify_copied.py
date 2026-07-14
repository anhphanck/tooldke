
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\code\extracted_data_debug.xlsx")
print("Sheet names:", xl.sheet_names)
for sheet_name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet_name)
    print(f"\n--- Sheet: {sheet_name} ---")
    print(df.to_string())
