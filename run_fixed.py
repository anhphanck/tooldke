
import os
import sys
import tempfile
from contextlib import contextmanager

# Step 1: Create our own temp directory and set TEMP/TMP to it
temp_dir = r"D:\dke\temp"
os.makedirs(temp_dir, exist_ok=True)
os.environ["TEMP"] = temp_dir
os.environ["TMP"] = temp_dir

# Step 2: Fix pytesseract before it's imported!
# We'll monkey-patch the necessary functions!
def fix_pytesseract():
    # First, let's import pytesseract
    import pytesseract
    from pytesseract import pytesseract as pt_module
    
    # Fix 1: Monkey-patch get_errors to use errors='replace'
    original_get_errors = pt_module.get_errors
    def fixed_get_errors(error_string):
        return original_get_errors(error_string.decode('utf-8', errors='replace').encode('utf-8'))
    pt_module.get_errors = fixed_get_errors
    
    # Fix 2: Monkey-patch the save function to use our temp dir
    original_save = pt_module.save
    @contextmanager
    def fixed_save(image):
        # Create a temporary file in our temp_dir with simple name
        fd, path = tempfile.mkstemp(suffix='.png', dir=temp_dir)
        os.close(fd)
        try:
            if isinstance(image, str):
                yield path, image
            else:
                # Save the image to our temp path
                image, extension = pt_module.prepare(image)
                temp_input = f"{path}_input.{extension}"
                image.save(temp_input, format=image.format)
                yield path, temp_input
        finally:
            # Clean up
            try:
                os.unlink(path)
                if 'temp_input' in locals():
                    os.unlink(temp_input)
            except:
                pass
    pt_module.save = fixed_save
    
    # Fix 3: Monkey-patch _read_output to use errors='replace'
    original_read_output = pt_module._read_output
    def fixed_read_output(filename, return_bytes=False):
        with open(filename, 'rb') as f:
            if return_bytes:
                return f.read()
            return f.read().decode('utf-8', errors='replace')
    pt_module._read_output = fixed_read_output

# Apply the fixes before importing extract_data_debug
fix_pytesseract()

# Now run extract_data_debug.py
sys.path.insert(0, r"D:\dke\tooldke")
exec(open(r"D:\dke\tooldke\extract_data_debug.py", encoding='utf-8').read())
