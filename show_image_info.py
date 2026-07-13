
from PIL import Image
import os

input_dir = r'D:\dke\10090-12'
files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

if files:
    first_file = files[0]
    img_path = os.path.join(input_dir, first_file)
    img = Image.open(img_path)
    print("File:", first_file)
    w, h = img.size
    print("Image size (Width x Height):", w, "x", h)
    print("\nNow open this image in Paint to measure coordinates (x1,y1) and (x2,y2)!")
    print("In Paint, current cursor coordinates are shown in the bottom-left corner!")
else:
    print("No PNG files found!")
