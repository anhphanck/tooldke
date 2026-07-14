
import pandas as pd
import os

code_dir = r"D:\dke\code"
for filename in os.listdir(code_dir):
    if filename.endswith('.xlsx') and not filename.startswith('~$'):
        print(f"\n--- Checking {filename} ---")
        try:
            xl = pd.ExcelFile(os.path.join(code_dir, filename))
            if 'T28' in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name='T28')
                print(df[df['Case'] == 11][['Case', 'Filename', 'Delta_t', 'Maximum', 'Mean', 'RMS']].head())
        except Exception as e:
            print(f"Error: {e}")
