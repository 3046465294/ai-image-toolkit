@echo off
echo ============================================
echo   AI Image Toolkit - Starting Server
echo ============================================
echo.

cd /d "%~dp0"

:: Check if .env exists
if not exist .env (
    echo [!] .env file not found!
    echo Please copy .env.example to .env and add your REPLICATE_API_TOKEN
    echo Get your token at: https://replicate.com/account/api-tokens
    pause
    exit /b 1
)

:: Install dependencies if needed
pip install -r requirements.txt -q

:: Start server
echo Starting server at http://localhost:5000
python app.py
pause
