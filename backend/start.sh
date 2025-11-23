#!/bin/bash
# Render deployment script
# This installs all dependencies and starts the backend

echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Starting backend server..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
