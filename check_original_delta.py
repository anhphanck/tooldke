
import pandas as pd

xl = pd.ExcelFile(r'D:\dke\tooldke\extracted_data.xlsx')
print("Checking original data:")
for sheet in ['T0', 'T8']:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f"\n--- {sheet} ---")
    print(df[['Case', 'Filename', 'Delta_t']].head(10))
