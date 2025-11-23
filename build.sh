#!/usr/bin/env bash
# Build script for Render deployment
# Install both Node.js and Python dependencies

echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Building frontend..."
npm install
npm run build

echo "Build complete!"
