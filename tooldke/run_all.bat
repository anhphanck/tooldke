
@echo off
cd /d "%~dp0"
echo Running custom_extract.py...
python custom_extract.py
echo.
echo Running replace_img_sheet_images.py...
python replace_img_sheet_images.py
echo.
echo Done! All files updated!
pause
