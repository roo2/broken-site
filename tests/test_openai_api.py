#!/usr/bin/env python3
"""
Test script to verify OpenAI API works with corrected tool format
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from diagnostics.agent import run_agent
from diagnostics.config import settings
import asyncio

def test_openai_api():
    """Test the OpenAI API with corrected tools"""
    
    print("🧪 Testing OpenAI API with Corrected Tools")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        print("   Please set your OpenAI API key in .env file")
        print("   Example: echo 'OPENAI_API_KEY=your_key_here' >> .env")
        return False
    
    print(f"✅ OpenAI API key found")
    print(f"✅ Using model: {settings.OPENAI_MODEL}")
    
    # Test with a simple domain
    test_target = "example.com"
    print(f"\n🎯 Testing with target: {test_target}")
    
    try:
        print("🔄 Calling OpenAI agent...")
        result = run_agent(test_target)
        
        print("✅ OpenAI agent executed successfully!")
        print(f"📊 Summary: {result.summary}")
        print(f"🔍 Issues found: {len(result.issues)}")
        
        if result.issues:
            print("\n📋 Issues:")
            for i, issue in enumerate(result.issues, 1):
                print(f"  {i}. {issue.category} - {issue.severity} severity")
        
        return True
        
    except Exception as e:
        print(f"❌ Error calling OpenAI agent: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_openai_api()
    if success:
        print("\n🎉 OpenAI API test passed!")
    else:
        print("\n💥 OpenAI API test failed!")
        sys.exit(1)
