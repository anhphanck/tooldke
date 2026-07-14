
from custom_extract import extract_values_from_image

image_path = r"D:\dke\10090-12\2026_07_09_10_19_01_11_case06_T10_P0.png"
values = extract_values_from_image(image_path)
print("Extracted values for T10 case 06:")
print(values)
