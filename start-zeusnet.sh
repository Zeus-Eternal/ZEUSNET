#!/bin/bash
set -e

echo "Starting ZeusNet Backend..."

cd "$(dirname "$0")"

# Activate virtualenv if present
if [ -d .venv ]; then
    source .venv/bin/activate
fi

# Kill any process on port 8000 (optional evil step)
# fuser -k 8000/tcp || true

# Start backend (Uvicorn) in background, log to file
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2 > backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting MQTT broker..."
docker compose up -d mqtt

echo "Starting ZeusNet Frontend..."
python3 frontend/main.py > frontend.log 2>&1 &
FRONTEND_PID=$!

# Graceful shutdown trap (optional)
trap "echo 'Shutting down...'; kill $BACKEND_PID; kill $FRONTEND_PID; docker compose down; exit" SIGINT SIGTERM

wait $FRONTEND_PID
