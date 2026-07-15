# Trích xuất dữ liệu từ ảnh sang Excel

Dự án dùng để trích xuất các giá trị (Delta_t, Maximum, Mean, RMS) từ ảnh chụp màn hình oscilloscope và tạo file Excel có sheet chứa ảnh được sắp xếp theo nhiệt độ.


## Yêu cầu

1. **Python 3.8+**
2. **Tesseract-OCR** (cài đặt tại `C:\Program Files\Tesseract-OCR\tesseract.exe`)
   - Tải về tại: https://github.com/UB-Mannheim/tesseract/wiki
   - Chọn phiên bản Windows (tesseract-ocr-w64-setup-v5.x.x.exe)
   - Cài đặt với đường dẫn mặc định


## Cài đặt

1. Clone repo về máy:
   ```bash
   git clone YOUR_REPO_URL
   cd dke1
   ```

2. Cài đặt các Python packages:
   - Đối với **Windows**: chỉ cần **đouble-click** vào file `install.bat`
   - Hoặc chạy thủ công:
     ```bash
     pip install -r requirements.txt
     ```


## Cấu trúc thư mục

```
dke1/
├── 10090-12/      # Chứa các ảnh PNG để xử lý
├── code/          # Chứa file Excel kết quả
├── tooldke/       # Mã nguồn chính
│   └── custom_extract.py
├── install.bat    # Script cài đặt nhanh cho Windows
├── requirements.txt
└── README.md
```


## Sử dụng

1. Đặt tất cả các ảnh PNG vào thư mục `10090-12/`
2. Chạy script:
   ```bash
   python tooldke/custom_extract.py
   ```
3. File Excel kết quả sẽ được tạo tại `code/extracted_data_final_v9.xlsx`


## Ghi chú

- Ảnh cần có tên chứa `caseXX` và `TYY` để phân nhóm đúng
- Sheet `img` trong Excel sẽ hiển thị ảnh được sắp xếp theo nhiệt độ (0°C, 10°C, 25°C, 40°C)
