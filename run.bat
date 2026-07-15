@echo off
chcp 65001 >nul
echo ========================================
echo   Chay script trich xuat du lieu
echo ========================================
echo.

cd /d "%~dp0"
python tooldke\custom_extract.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   CO LOI XAY RA!
    echo ========================================
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo   HOAN TAT!
echo   File Excel da duoc tao trong thu muc code
echo ========================================
echo.
pause
