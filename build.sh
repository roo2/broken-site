#!/bin/bash

# Build the frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

echo "Build completed!"
