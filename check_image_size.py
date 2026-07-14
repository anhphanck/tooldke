
from PIL import Image

img_path = r"D:\dke\10090-12\2026_07_11_09_10_05_11_case01_T0_P0.png"
img = Image.open(img_path)
print(f"Image size: {img.size} (width, height)")
print(f"Image mode: {img.mode}")
