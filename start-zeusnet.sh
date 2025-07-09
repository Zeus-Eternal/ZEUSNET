#!/bin/bash

set -e

echo "Starting ZeusNet Backend..."
cd backend
if [ -d ../.venv ]; then
    source ../.venv/bin/activate
fi
if [ "$ZEUSNET_ENV" = "dev" ]; then
    uvicorn main:app --reload &
else
    uvicorn main:app --host 0.0.0.0 --port 8000 &
fi
cd ..

echo "Starting MQTT broker..."
docker compose up -d mqtt

echo "Starting ZeusNet Frontend..."
python frontend/main.py &
wait

