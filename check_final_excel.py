
import pandas as pd

xl = pd.ExcelFile(r"D:\dke\code\extracted_data_final.xlsx")
print("Sheets in final Excel:", xl.sheet_names)
print("\n--- T0 sheet head ---")
df_t0 = pd.read_excel(xl, sheet_name="T0")
print(df_t0.head())
print("\n--- T8 sheet head ---")
df_t8 = pd.read_excel(xl, sheet_name="T8")
print(df_t8.head())
print("\n--- T8 sheet Delta_t values ---")
print(df_t8[["Case", "Filename", "Delta_t"]])
