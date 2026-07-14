
from custom_extract import ocr_region
from PIL import Image

image_path = r"D:\dke\10090-12\2026_07_09_10_20_33_11_case11_T28_P0.png"
img = Image.open(image_path)
delta_t_bbox = (400,20,1500,220)
meas_bbox = (1500,120,1920,650)

delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
meas_text = ocr_region(img, meas_bbox, config='--psm 6')

print("=== Delta_t region OCR text ===")
print(repr(delta_t_text))
print("\n=== Meas region OCR text ===")
print(repr(meas_text))
