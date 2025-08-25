#!/usr/bin/env bash
set -euo pipefail

# Build the frontend
echo "Building frontend..."
cd frontend
npm ci --no-audit --no-fund
npm run build
cd ..

# Ensure Python deps installed
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

echo "Build complete"
