
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\code\extracted_data_final_v6.xlsx")
df = pd.read_excel(xl, sheet_name='T40')
print("=== T40 Sheet ===")
print(df)
