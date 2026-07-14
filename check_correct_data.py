
import pandas as pd

xl = pd.ExcelFile(r'D:\dke\code\extracted_data_final.xlsx')
print("Checking extracted_data_final.xlsx:")
for sheet in ['T0', 'T8']:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f"\n--- {sheet} ---")
    print(df[['Case', 'Filename', 'Delta_t', 'Maximum', 'Mean', 'RMS']].head(10))
