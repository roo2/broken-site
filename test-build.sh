#!/bin/bash

echo "🧪 Testing build process locally..."

# Test frontend build
echo "🔨 Testing frontend build..."
cd frontend
if [ -f "build.sh" ]; then
    echo "✅ Frontend build script exists"
    bash build.sh
    if [ -d "dist" ]; then
        echo "✅ Frontend build successful - dist directory created"
        echo "📁 Dist contents:"
        ls -la dist/
    else
        echo "❌ Frontend build failed"
        exit 1
    fi
else
    echo "❌ Frontend build script not found"
    exit 1
fi
cd ..

echo "🎉 Build test completed successfully!"
