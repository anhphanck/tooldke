@echo off
echo ========================================
echo   Cai dat cac dependency cho du an
echo ========================================
echo.

echo [1/2] Upgrade pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Loi khi upgrade pip!
    pause
    exit /b %errorlevel%
)
echo.

echo [2/2] Cai dat cac package tu requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Loi khi cai dat cac package!
    pause
    exit /b %errorlevel%
)
echo.

echo ========================================
echo   Cai dat hoan tat!
echo ========================================
echo.
echo Ban dang san sang chay script!
echo Vui long kiem tra ban da cai dat Tesseract-OCR tai C:\Program Files\Tesseract-OCR
echo.
pause
