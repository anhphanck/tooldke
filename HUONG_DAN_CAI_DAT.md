
# Hướng dẫn cài đặt và sử dụng tool trích xuất dữ liệu

## Bước 1: Cài đặt Python
1. Tải Python từ https://www.python.org/downloads/
2. Khi cài đặt, nhớ tích chọn "Add Python to PATH"
3. Kiểm tra cài đặt bằng lệnh trong PowerShell: `python --version`

## Bước 2: Cài đặt Tesseract OCR
1. Tải Tesseract từ https://github.com/UB-Mannheim/tesseract/wiki
2. Cài đặt vào thư mục mặc định: `C:\Program Files\Tesseract-OCR`
3. Thêm `C:\Program Files\Tesseract-OCR` vào biến môi trường PATH của Windows

## Bước 3: Cài đặt các gói Python cần thiết
Mở PowerShell và chạy lệnh:
```
pip install pillow pytesseract pandas openpyxl
```

## Bước 4: Chạy script
Trong thư mục `D:\dke\code`, chạy lệnh:
```
python extract_data.py
```

Kết quả sẽ được lưu vào file `extracted_data.xlsx`
