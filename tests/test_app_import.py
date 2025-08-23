#!/usr/bin/env python3
"""
Test script to verify FastAPI app import works correctly
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from diagnostics.main import app
    print("✅ FastAPI app imported successfully!")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    
    # List available routes
    print("\n📋 Available routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.methods} {route.path}")
    
    print("\n🚀 App is ready to run!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
