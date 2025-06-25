@echo off

cd backend
if exist ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
)
start uvicorn main:app --reload
cd ..

docker compose up -d mqtt

cd frontend
npm run dev

