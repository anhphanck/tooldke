import os
import re
from PIL import Image
import pytesseract
import pandas as pd

# Configure Tesseract path (nếu Tesseract không nằm trong PATH)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_info_from_filename(filename):
    """Trích xuất số case và giá trị T từ tên file"""
    pattern = r'case(\d+)_T(\d+)'
    match = re.search(pattern, filename)
    if match:
        case = int(match.group(1))
        t_value = int(match.group(2))
        return case, t_value
    return None, None

def ocr_region(img, bbox, config='--psm 6'):
    """Thực hiện OCR trên một vùng cụ thể của ảnh"""
    cropped = img.crop(bbox)
    # Tiền xử lý ảnh: chỉ chuyển sang grayscale, không áp dụng threshold
    gray = cropped.convert('L')
    text = pytesseract.image_to_string(gray, config=config)
    return text.strip()

def extract_values_from_image(image_path):
    """Trích xuất Δt, Maximum, Mean và RMS từ ảnh bằng OCR"""
    try:
        # Mở ảnh
        img = Image.open(image_path)
        width, height = img.size
        
        # ---------- ĐIỀU CHỈNH CÁC GIÁ TRỊ BBOX NÀY CHO PHÙ HỢP VỚI ẢNH CỦA BẠN ----------
        # Dành cho ảnh 1920x1080 - mở rộng vùng nhiều hơn nữa
        delta_t_bbox = (400, 20, 1500, 220)
        meas_bbox = (1500, 120, 1920, 650)
        # ----------------------------------------------------------------------------
        
        # Thực hiện OCR trên từng vùng
        delta_t_text = ocr_region(img, delta_t_bbox, config='--psm 12')
        meas_text = ocr_region(img, meas_bbox, config='--psm 6')
        
        # Kết hợp văn bản
        full_text = delta_t_text + "\n" + meas_text
        
        # Phân tích các giá trị
        values = {}
        
        def clean_number(s):
            """Loại bỏ dấu chấm/phẩy thừa ở đầu và cuối trước khi chuyển sang float"""
            s = s.replace(',', '.').strip('.')
            return float(s)
        
        # Tìm Δt: ưu tiên giá trị kèm theo đơn vị 's' (giây), nếu không thì tìm số bất kỳ trong vùng
        delta_t_match = re.search(r'([\d.,]+)\s*s', delta_t_text, re.IGNORECASE)
        if not delta_t_match:
            # Fallback: tìm tất cả số trong vùng delta_t, chọn số có vẻ hợp lý (không quá nhỏ, không quá lớn)
            numbers = re.findall(r'[\d.,]+', delta_t_text)
            for num_str in numbers:
                try:
                    num = clean_number(num_str)
                    if 10 < num < 1000:  # Giả sử Δt trong khoảng này
                        values['Delta_t'] = num
                        break
                except:
                    pass
        else:
            values['Delta_t'] = clean_number(delta_t_match.group(1))
        
        # Tìm Maximum, Mean, RMS - hỗ trợ cả dấu phẩy và dấu chấm làm phân cách thập phân
        max_match = re.search(r'Maximum[^\d]*([\d.,]+)', meas_text, re.IGNORECASE)
        if max_match:
            values['Maximum'] = clean_number(max_match.group(1))
        
        mean_match = re.search(r'Mean[^\d]*([\d.,]+)', meas_text, re.IGNORECASE)
        if mean_match:
            values['Mean'] = clean_number(mean_match.group(1))
        
        rms_match = re.search(r'RMS[^\d]*([\d.,]+)', meas_text, re.IGNORECASE)
        if rms_match:
            values['RMS'] = clean_number(rms_match.group(1))
        
        return values
    except Exception as e:
        print(f"Lỗi khi xử lý {image_path}: {e}")
        return {}

def main():
    # Thư mục chứa ảnh đầu vào
    input_dir = r'D:\dke\10090-12'
    
    # File Excel đầu ra
    output_file = r'D:\dke\code\extracted_data.xlsx'
    
    # Từ điển lưu dữ liệu theo giá trị T
    t_data = {}
    
    # Xử lý tất cả file PNG
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(input_dir, filename)
            case, t_value = extract_info_from_filename(filename)
            
            if t_value is not None:
                # Trích xuất giá trị từ ảnh
                image_values = extract_values_from_image(file_path)
                
                # Khởi tạo nhóm T nếu cần
                t_key = f"T{t_value}"
                if t_key not in t_data:
                    t_data[t_key] = []
                
                # Thêm bản ghi, sắp xếp thứ tự cột
                entry = {
                    'Case': case,
                    'Filename': filename,
                    'Delta_t': image_values.get('Delta_t'),
                    'Maximum': image_values.get('Maximum'),
                    'Mean': image_values.get('Mean'),
                    'RMS': image_values.get('RMS')
                }
                t_data[t_key].append(entry)
                print(f"Đã xử lý {filename} - T{t_value}")
    
    # Ghi vào Excel, mỗi giá trị T một sheet (sắp xếp sheet từ nhỏ đến lớn)
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sắp xếp các sheet theo giá trị T (ví dụ: T0, T2, T4,...)
        sorted_t_keys = sorted(t_data.keys(), key=lambda x: int(x.replace('T', '')))
        for t_key in sorted_t_keys:
            df = pd.DataFrame(t_data[t_key])
            # Sắp xếp các hàng theo Case
            df = df.sort_values(by='Case')
            df.to_excel(writer, sheet_name=t_key, index=False)
            print(f"Đã ghi sheet {t_key}")
    
    print(f"\nHoàn thành! Dữ liệu được lưu vào {output_file}")

if __name__ == "__main__":
    main()
