
from custom_extract import extract_values_from_image

image_path = r"D:\dke\10090-12\2026_07_09_10_35_31_11_case11_T28_P0.png"
values = extract_values_from_image(image_path)
print("Extracted values for T28 case 11:")
print(values)
