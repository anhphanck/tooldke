
from custom_extract import ocr_region
from PIL import Image
import re
from custom_extract import clean_number

image_path = r"D:\dke\10090-12\2026_07_09_10_19_01_11_case06_T10_P0.png"
img = Image.open(image_path)
delta_t_bbox = (0, 0, 1920, 400)
meas_bbox = (1500,120,1920,650)

delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')

print("=== delta_t_text ===")
print(repr(delta_t_text))

print("\n=== Testing all regex patterns ===")
t_match = re.search(r'\bt[^\d]*([\d.,]+)\s*s', delta_t_text, re.IGNORECASE)
if t_match:
    print(f"t_match found: {clean_number(t_match.group(1))}")
else:
    print("t_match not found")

print("\n=== All s matches ===")
for match in re.finditer(r'([\d.,]+)\s*s', delta_t_text, re.IGNORECASE):
    print(f"  Found s match: {match.group(1)} at {match.span()}")
    match_start, _ = match.span()
    context = delta_t_text[max(0, match_start - 20):match_start+10]
    print(f"  Context: {repr(context)}")

print("\n=== All numbers ===")
numbers = re.findall(r'[\d.,]+', delta_t_text)
for num_str in numbers:
    try:
        num = clean_number(num_str)
        print(f"  Number: {num}")
    except Exception as e:
        print(f"  Couldn't clean {num_str}: {e}")
