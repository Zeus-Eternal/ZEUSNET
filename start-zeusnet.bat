@echo off

cd backend
if exist ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
)
if "%ZEUSNET_ENV%"=="dev" (
    start uvicorn main:app --reload
) else (
    start uvicorn main:app --host 0.0.0.0 --port 8000
)
cd ..

docker compose up -d mqtt

python frontend/main.py

