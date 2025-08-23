#!/bin/bash

echo "Starting backend server..."
echo "Backend will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the backend server
uvicorn src.diagnostics.main:app --reload --host 0.0.0.0 --port 8000
