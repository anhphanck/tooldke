
import pandas as pd

xl = pd.ExcelFile(r'D:\dke\code\extracted_data_complete.xlsx')
df = pd.read_excel(xl, sheet_name='T0')
print("T0 sheet:")
print(df.to_string())
