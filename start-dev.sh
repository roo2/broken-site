#!/bin/bash

# Start both backend and frontend development servers
# Usage: ./start-dev.sh

echo "🚀 Starting BrokenSite Development Environment"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Please run:"
    echo "   cd frontend && npm install"
    exit 1
fi

echo "✅ Starting backend server on http://localhost:8000"
echo "✅ Starting frontend server on http://localhost:3000"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "🔍 Logging: Set LOG_LEVEL=INFO in .env for detailed logs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
source .venv/bin/activate
uvicorn diagnostics.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
