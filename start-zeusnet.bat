@echo off

cd backend
if exist ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
)
start uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
cd ..

docker compose up -d mqtt

python frontend/main.py

