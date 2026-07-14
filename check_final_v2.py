
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\code\extracted_data_final_v6.xlsx")
for sheet_name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet_name)
    print(f"\n=== Sheet {sheet_name} ===")
    print(df[['Case', 'Delta_t', 'Maximum', 'Mean', 'RMS']].head())
