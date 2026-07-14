
from custom_extract import ocr_region, clean_number, extract_values_from_image
from PIL import Image
import re

image_path = r"D:\dke\10090-12\2026_07_09_12_15_40_11_case06_T10_P0.png"
img = Image.open(image_path)
delta_t_bbox = (0, 0, 1920, 400)
delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')

print("=== delta_t_text ===")
print(repr(delta_t_text))

print("\n=== Testing t_match finditer ===")
for t_match in re.finditer(r'\bt[:\s]+[^\d]*([\d.,]+)', delta_t_text, re.IGNORECASE):
    num_str = t_match.group(1)
    print(f"  t_match found: num_str={repr(num_str)}, span={t_match.span()}")
    num = clean_number(num_str)
    print(f"  num={num}")
    if num is not None and num > 0:
        match_start, match_end = t_match.span()
        context_before = delta_t_text[max(0, match_start -15):match_start].lower()
        context_after = delta_t_text[match_end:match_end +15].lower()
        print(f"  context_before={repr(context_before)}")
        print(f"  context_after={repr(context_after)}")
        print(f"  at in before? {'at' in context_before}")
        print(f"  ms in after? {'ms' in context_after}")
        print(f"  hz in after? {'hz' in context_after}")
        print(f"  mhz in after? {'mhz' in context_after}")

print("\n=== extract_values_from_image ===")
values = extract_values_from_image(image_path)
print(values)
