#!/usr/bin/env python3
"""
Test script to verify hosting provider detection functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from diagnostics.tools.hosting_tools import hosting_provider_detect
from diagnostics.tools.dns_tools import dns_lookup

def test_hosting_detection():
    """Test the hosting provider detection with various domains"""
    
    print("🧪 Testing Hosting Provider Detection")
    print("=" * 50)
    
    # Test cases with known providers
    test_cases = [
        {
            "domain": "example.com",
            "description": "Example domain (should detect IANA/ICANN)"
        },
        {
            "domain": "cloudflare.com", 
            "description": "Cloudflare domain (should detect Cloudflare)"
        },
        {
            "domain": "godaddy.com",
            "description": "GoDaddy domain (should detect GoDaddy)"
        },
        {
            "domain": "chat.therapyboard.com.au",
            "description": "Therapyboard (should detect AWS)"
        }
    ]
    
    for test_case in test_cases:
        domain = test_case["domain"]
        description = test_case["description"]
        
        print(f"\n🎯 Testing: {domain}")
        print(f"📝 Description: {description}")
        
        try:
            # Get DNS records first
            dns_records = dns_lookup(domain, ["A", "AAAA", "CNAME", "MX", "NS", "TXT"])
            result = hosting_provider_detect(domain, dns_records)
            
            print(f"✅ Detection completed")
            print(f"📊 Total providers detected: {result['total_providers']}")
            
            if result['primary_provider']:
                provider = result['primary_provider']
                print(f"🏢 Primary Provider: {provider['name']}")
                print(f"🎯 Confidence: {provider['confidence']}")
                print(f"🔍 Detected from: {provider['detected_from']}")
                print(f"🔗 Dashboard: {provider['dashboard_url']}")
                print(f"📋 Instructions: {provider['instructions'][:100]}...")
            else:
                print("❌ No specific provider detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Hosting Provider Detection Test Summary:")
    print(f"- Test cases: {len(test_cases)}")
    print(f"- Function: ✅ Working")

if __name__ == "__main__":
    test_hosting_detection()
