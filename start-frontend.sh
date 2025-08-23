#!/bin/bash

echo "Starting frontend development server..."
echo "Frontend will be available at: http://localhost:5173"
echo ""

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found!"
    echo "Please make sure you're in the project root directory."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists, install if not
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start the frontend development server
npm run dev
