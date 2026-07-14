
import pandas as pd

xl = pd.ExcelFile(r'D:\dke\code\extracted_data_complete.xlsx')
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f'--- {sheet} ---')
    print('Missing values:')
    print(df.isnull().sum())
    print()
