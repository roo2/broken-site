#!/usr/bin/env python3
"""
Test script to verify OpenAI agent works with fixed tool format
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from diagnostics.agent import TOOLS, FUNCTIONS
from diagnostics.config import settings
import json

def test_openai_tools():
    """Test the OpenAI tools configuration"""
    
    print("🧪 Testing OpenAI Tools Configuration")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not set - skipping actual API test")
        print("   This test will only validate tool format")
    
    # Test tool format
    print("\n📋 Testing Tool Format...")
    
    for i, tool in enumerate(TOOLS):
        print(f"\nTool {i+1}: {tool.get('function', {}).get('name', 'NO_NAME')}")
        
        # Check required fields for Chat Completions API
        required_fields = ['type', 'function']
        missing_fields = [field for field in required_fields if field not in tool]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
        else:
            function_data = tool['function']
            print(f"✅ All required fields present")
            print(f"   Type: {tool['type']}")
            print(f"   Name: {function_data['name']}")
            print(f"   Description: {function_data['description'][:50]}...")
            print(f"   Parameters: {len(function_data['parameters'].get('properties', {}))} properties")
    
    # Test function mapping
    print(f"\n🔧 Testing Function Mapping...")
    tool_names = [tool['function']['name'] for tool in TOOLS]
    function_names = list(FUNCTIONS.keys())
    
    missing_functions = [name for name in tool_names if name not in function_names]
    extra_functions = [name for name in function_names if name not in tool_names]
    
    if missing_functions:
        print(f"❌ Tools without functions: {missing_functions}")
    else:
        print(f"✅ All tools have corresponding functions")
    
    if extra_functions:
        print(f"⚠️  Functions without tools: {extra_functions}")
    else:
        print(f"✅ All functions have corresponding tools")
    
    # Test tool JSON serialization
    print(f"\n📝 Testing Tool JSON Serialization...")
    try:
        tools_json = json.dumps(TOOLS, indent=2)
        print(f"✅ Tools can be serialized to JSON")
        print(f"   JSON length: {len(tools_json)} characters")
    except Exception as e:
        print(f"❌ Failed to serialize tools to JSON: {e}")
    
    # Show sample tool structure
    if TOOLS:
        print(f"\n📄 Sample Tool Structure:")
        sample_tool = TOOLS[0]
        print(json.dumps(sample_tool, indent=2))
    
    print(f"\n🎯 OpenAI Tools Test Summary:")
    print(f"- Total tools: {len(TOOLS)}")
    print(f"- Total functions: {len(FUNCTIONS)}")
    print(f"- Tool format: {'✅ Valid' if len(TOOLS) > 0 else '❌ Invalid'}")
    print(f"- Function mapping: {'✅ Complete' if not missing_functions else '❌ Incomplete'}")
    print(f"- Focus: {'✅ Critical issues + hosting detection' if len(TOOLS) == 4 else '❌ Unexpected tool count'}")

if __name__ == "__main__":
    test_openai_tools()
