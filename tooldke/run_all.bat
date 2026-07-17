
@echo off
cd /d d:\dke3\tooldke
echo Running custom_extract.py...
python custom_extract.py
echo.
echo Running convert_and_add_averages.py...
python convert_and_add_averages.py
echo.
echo Done! Both files updated.
pause
