#!/usr/bin/env python3
"""
Test script to verify both offline and OpenAI modes work correctly
"""
import sys
import os
import requests
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from diagnostics.config import settings

def test_api_modes():
    """Test both offline and OpenAI modes"""
    
    base_url = "http://localhost:8000"
    test_url = "https://example.com"
    
    print("🧪 Testing API Modes")
    print("=" * 50)
    
    # Test offline mode
    print("\n📋 Testing Offline Mode...")
    try:
        response = requests.post(
            f"{base_url}/diagnose/user-friendly?mode=offline",
            json={"target": test_url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Offline mode works!")
            print(f"   Is Broken: {data.get('is_broken')}")
            print(f"   User Message: {data.get('user_message')}")
            if data.get('primary_issue'):
                print(f"   Primary Issue: {data['primary_issue']['title']}")
        else:
            print(f"❌ Offline mode failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Offline mode error: {e}")
    
    # Test OpenAI mode
    print("\n🤖 Testing OpenAI Mode...")
    if not settings.OPENAI_API_KEY:
        print("⚠️  OpenAI API key not set - this test will fail")
    
    try:
        response = requests.post(
            f"{base_url}/diagnose/user-friendly?mode=openai",
            json={"target": test_url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OpenAI mode works!")
            print(f"   Is Broken: {data.get('is_broken')}")
            print(f"   User Message: {data.get('user_message')}")
            if data.get('primary_issue'):
                print(f"   Primary Issue: {data['primary_issue']['title']}")
        elif response.status_code == 400:
            print("⚠️  OpenAI mode failed as expected (no API key)")
            print("   This is correct behavior when API key is missing")
        else:
            print(f"❌ OpenAI mode failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ OpenAI mode error: {e}")
    
    print("\n🎯 Test Summary:")
    print("- Offline mode should always work")
    print("- OpenAI mode requires OPENAI_API_KEY to be set")
    print("- Both modes return the same user-friendly format")

if __name__ == "__main__":
    test_api_modes()
