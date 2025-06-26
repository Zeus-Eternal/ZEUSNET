#!/bin/bash

set -e

echo "Starting ZeusNet Backend..."
cd backend
if [ -d ../.venv ]; then
    source ../.venv/bin/activate
fi
uvicorn main:app --reload &
cd ..

echo "Starting MQTT broker..."
docker compose up -d mqtt

echo "Starting ZeusNet Frontend..."
cd frontend
npm run dev

