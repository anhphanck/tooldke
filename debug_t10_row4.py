
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\code\extracted_data_final_v5.xlsx")
df = pd.read_excel(xl, sheet_name='T10')
print("=== T10 Sheet ===")
print(df[['Case', 'Filename', 'Delta_t', 'Maximum', 'Mean', 'RMS']])
