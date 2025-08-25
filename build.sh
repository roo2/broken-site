#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting build process..."

# Check current directory
echo "📁 Current directory: $(pwd)"

# Build the frontend
echo "🔨 Building frontend..."
cd frontend
echo "📁 Frontend directory: $(pwd)"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

echo "📦 Installing npm dependencies..."
npm install

echo "🏗️ Building frontend with Vite..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Frontend build failed - dist directory not created"
    exit 1
fi

echo "✅ Frontend build completed successfully"
echo "📁 Dist directory contents:"
ls -la dist/

cd ..

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

echo "🎉 Build completed successfully!"
