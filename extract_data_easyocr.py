
import os
import re
import easyocr
import pandas as pd
from PIL import Image

# Khởi tạo reader EasyOCR (dùng ngôn ngữ tiếng Anh)
reader = easyocr.Reader(['en'])

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
        
        # Vùng cần trích xuất (đã mở rộng tối đa cho ảnh 1920x1080)
        delta_t_bbox = (300, 10, 1600, 250)
        meas_bbox = (1450, 100, 1920, 700)
        
        def ocr_region(bbox):
            left, top, right, bottom = bbox
            cropped = img.crop((left, top, right, bottom))
            results = reader.readtext(cropped, detail=0)  # detail=0 chỉ trả về text
            return ' '.join(results)
        
        delta_t_text = ocr_region(delta_t_bbox)
        meas_text = ocr_region(meas_bbox)
        full_text = delta_t_text + ' ' + meas_text
        
        values = {}
        
        def clean_number(s):
            s = s.replace(',', '.').strip('.')
            return float(s)
        
        # Tìm Delta_t (ưu tiên có 's', fallback tìm số hợp lý)
        delta_t_match = re.search(r'([\d.,]+)\s*s', delta_t_text, re.IGNORECASE)
        if not delta_t_match:
            numbers = re.findall(r'[\d.,]+', delta_t_text)
            for num_str in numbers:
                try:
                    num = clean_number(num_str)
                    if 10 < num < 1000:
                        values['Delta_t'] = num
                        break
                except:
                    pass
        else:
            values['Delta_t'] = clean_number(delta_t_match.group(1))
        
        # Tìm Maximum, Mean, RMS
        max_match = re.search(r'Maximum[^\d]*([\d.,]+)', full_text, re.IGNORECASE)
        if max_match:
            values['Maximum'] = clean_number(max_match.group(1))
        
        mean_match = re.search(r'Mean[^\d]*([\d.,]+)', full_text, re.IGNORECASE)
        if mean_match:
            values['Mean'] = clean_number(mean_match.group(1))
        
        rms_match = re.search(r'RMS[^\d]*([\d.,]+)', full_text, re.IGNORECASE)
        if rms_match:
            values['RMS'] = clean_number(rms_match.group(1))
        
        return values
    except Exception as e:
        print(f"Lỗi khi xử lý {image_path}: {e}")
        return {}

def main():
    input_dir = r'D:\dke\10090-12'
    output_file = r'D:\dke\code\extracted_data_easyocr.xlsx'
    
    t_data = {}
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(input_dir, filename)
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
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        sorted_t_keys = sorted(t_data.keys(), key=lambda x: int(x.replace('T', '')))
        for t_key in sorted_t_keys:
            df = pd.DataFrame(t_data[t_key])
            df = df.sort_values(by='Case')
            df.to_excel(writer, sheet_name=t_key, index=False)
            print(f"Đã ghi sheet {t_key}")
    
    print(f"\nHoàn thành! Dữ liệu được lưu vào {output_file}")

if __name__ == "__main__":
    main()
