
from custom_extract import ocr_image, extract_values

image_path = r"D:\dke\10090-12\2026_07_09_10_17_50_11_case05_T8_P0.png"
ocr_text = ocr_image(image_path)
print("OCR Text:", repr(ocr_text))
values = extract_values(ocr_text)
print("Extracted Values:", values)
