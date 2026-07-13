
from PIL import Image
import os

def check_first_image():
    input_dir = r'D:\dke\10090-12'
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
    if files:
        first_file = os.path.join(input_dir, files[0])
        img = Image.open(first_file)
        print(f"Kích thước ảnh: {img.size} (width x height)")
        print(f"File: {first_file}")
        print("\nBạn có thể dùng thông tin này để điều chỉnh bbox trong extract_data.py")
        return img
    else:
        print("Không tìm thấy file PNG nào trong thư mục")
        return None

if __name__ == "__main__":
    check_first_image()
