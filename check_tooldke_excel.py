
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\tooldke\extracted_data.xlsx")
if 'T28' in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name='T28')
    print(df[df['Case'] == 11][['Case', 'Filename', 'Delta_t', 'Maximum', 'Mean', 'RMS']])
