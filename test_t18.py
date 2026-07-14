
from custom_extract import extract_values_from_image

image_path = r"D:\dke\10090-12\2026_07_09_10_54_48_11_case08_T18_P0.png"
values = extract_values_from_image(image_path)
print("Extracted values for T18 case 08:")
print(values)
