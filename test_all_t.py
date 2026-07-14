import os
import sys
sys.path.insert(0, r'd:\dke')
from custom_extract import extract_values_from_image

IMAGE_DIR = r"D:\dke\10090-12"

# Get all unique T labels
image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(".png")]
t_labels = set()
for f in image_files:
    import re
    match = re.search(r'_(T\d+)_', f)
    if match:
        t_labels.add(match.group(1))
t_labels = sorted(t_labels, key=lambda x: int(x[1:]))
print(f"Testing all T labels: {t_labels}")

for t_label in t_labels:
    print(f"\n=== Testing {t_label} ===")
    t_files = [f for f in image_files if f"_{t_label}_" in f]
    for filename in t_files[:1]:  # Test just first file for each T
        print(f"  File: {filename}")
        image_path = os.path.join(IMAGE_DIR, filename)
        values = extract_values_from_image(image_path)
        print(f"  Values: {values}")
