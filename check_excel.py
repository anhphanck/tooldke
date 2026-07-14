
import pandas as pd

xls = pd.ExcelFile('code/extracted_data_debug.xlsx')
print('Sheet names:', xls.sheet_names)
for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    print(f'\nSheet {sheet}:')
    print(df)
