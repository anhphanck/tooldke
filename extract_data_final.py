
import os
import re
import pytesseract
import pandas as pd
from PIL import Image

# ===================== CẤU HÌNH =====================
# Đường dẫn thư mục chứa ảnh PNG
INPUT_DIR = r'D:\dke\10090-12'
# Đường dẫn file Excel đầu ra
OUTPUT_FILE = r'D:\dke\code\extracted_data.xlsx'
# Đường dẫn tesseract.exe (nếu không có trong PATH)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# =====================================================

# Configure Tesseract path
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_info_from_filename(filename):
    pattern = r'case(\d+)_T(\d+)'
    match = re.search(pattern, filename)
    if match:
        case = int(match.group(1))
        t_value = int(match.group(2))
        return case, t_value
    return None, None

def extract_values_from_image(image_path):
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # 2 vùng riêng:
        # Vùng chứa Δt: toàn bộ trên 1/3 ảnh
        delta_t_bbox = (0, 0, width, height // 3)
        meas_bbox = (width - 600, height // 6, width, height // 1.5)  # Vùng chứa Meas 1-3 (mở rộng)
        
        def ocr_region(bbox, config='--psm 11'):
            left, top, right, bottom = bbox
            cropped = img.crop((left, top, right, bottom))
            gray = cropped.convert('L')
            text = pytesseract.image_to_string(gray, config=config)
            return text
        
        delta_t_text = ocr_region(delta_t_bbox)
        meas_text = ocr_region(meas_bbox, config='--psm 6')  # Dùng psm 6 cho meas region
        
        values = {
            'Delta_t': None,
            'Maximum': None,
            'Mean': None,
            'RMS': None
        }
        
        def clean_number(s):
            # Chỉ giữ lại chữ số và dấu thập phân
            cleaned = re.sub(r'[^\d.,]', '', s)
            cleaned = cleaned.replace(',', '.').strip('.')
            try:
                return float(cleaned)
            except:
                return None
        
        # 1. Tìm Delta_t: ưu tiên "Δt:" hoặc "At:" trước, sau đó mới "t:"
        delta_t_match = re.search(r'(?:Δt|At)\s*:\s*([\d.,]+)\s*[s]', delta_t_text, re.IGNORECASE)
        if not delta_t_match:
            delta_t_match = re.search(r'(?:Δt|At)\s*:\s*([\d.,]+)', delta_t_text, re.IGNORECASE)
        if not delta_t_match:
            delta_t_match = re.search(r't\s*:\s*([\d.,]+)\s*[s]', delta_t_text, re.IGNORECASE)
        if not delta_t_match:
            delta_t_match = re.search(r't\s*:\s*([\d.,]+)', delta_t_text, re.IGNORECASE)
        if not delta_t_match:
            # Fallback: tìm số có khoảng 10-100 trong delta_t region, ưu tiên số có dấu thập phân
            numbers = re.findall(r'(\d+(?:[.,]\d+))', delta_t_text)
            for num_str in numbers:
                num = clean_number(num_str)
                if num and 10 < num < 100:
                    values['Delta_t'] = num
                    break
        else:
            values['Delta_t'] = clean_number(delta_t_match.group(1))
        
        # 2. Tìm Maximum, Mean, RMS theo thứ tự Meas 1, Meas 2, Meas 3
        # Tách meas_text thành các phần Meas 1, Meas 2, Meas 3
        meas_parts = re.split(r'Meas\s+\d+', meas_text, flags=re.IGNORECASE)
        # meas_parts[0] là trước Meas 1, meas_parts[1] là Meas 1, meas_parts[2] là Meas 2, meas_parts[3] là Meas 3
        
        if len(meas_parts) >= 2:
            # Meas 1: Maximum
            max_part = meas_parts[1]
            max_numbers = re.findall(r'(\d+(?:[.,]\d+))', max_part)
            if max_numbers:
                # Lấy số có giá trị lớn nhất cho Maximum (vì Maximum thường lớn hơn Mean/RMS)
                max_candidates = [clean_number(n) for n in max_numbers if clean_number(n) is not None]
                if max_candidates:
                    values['Maximum'] = max(max_candidates)
        
        if len(meas_parts) >= 3:
            # Meas 2: Mean
            mean_part = meas_parts[2]
            mean_numbers = re.findall(r'(\d+(?:[.,]\d+))', mean_part)
            if mean_numbers:
                mean_candidates = [clean_number(n) for n in mean_numbers if clean_number(n) is not None]
                if mean_candidates:
                    values['Mean'] = mean_candidates[0]
        
        if len(meas_parts) >= 4:
            # Meas 3: RMS
            rms_part = meas_parts[3]
            rms_numbers = re.findall(r'(\d+(?:[.,]\d+))', rms_part)
            if rms_numbers:
                rms_candidates = [clean_number(n) for n in rms_numbers if clean_number(n) is not None]
                if rms_candidates:
                    values['RMS'] = rms_candidates[0]
        
        return values
    except Exception as e:
        print(f"Lỗi khi xử lý {image_path}: {e}")
        import traceback
        traceback.print_exc()
        return {}

def main():
    t_data = {}
    
    if not os.path.exists(INPUT_DIR):
        print(f"Lỗi: Thư mục {INPUT_DIR} không tồn tại!")
        return
    
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(INPUT_DIR, filename)
            case, t_value = extract_info_from_filename(filename)
            
            if t_value is not None:
                image_values = extract_values_from_image(file_path)
                
                t_key = f"T{t_value}"
                if t_key not in t_data:
                    t_data[t_key] = []
                
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
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        sorted_t_keys = sorted(t_data.keys(), key=lambda x: int(x.replace('T', '')))
        for t_key in sorted_t_keys:
            df = pd.DataFrame(t_data[t_key])
            df = df.sort_values(by='Case')
            df.to_excel(writer, sheet_name=t_key, index=False)
            print(f"Đã ghi sheet {t_key}")
    
    print(f"\nHoàn thành! Dữ liệu được lưu vào {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
