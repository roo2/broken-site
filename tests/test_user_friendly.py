#!/usr/bin/env python3
"""
Test script to demonstrate user-friendly issue conversion
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from diagnostics.user_friendly import convert_to_user_friendly
from diagnostics.schemas import Issue
from rich import print

def test_user_friendly_conversion():
    """Test the user-friendly conversion with different issue types"""
    
    # Test cases
    test_cases = [
        {
            "name": "DNS Lookup Error (Broken Site)",
            "issues": [
                Issue(
                    id="dns_a_lookup_error",
                    category="DNS",
                    severity="high",
                    evidence="A lookup error: NXDOMAIN",
                    recommended_fix="Verify domain exists and is publicly resolvable"
                )
            ]
        },
        {
            "name": "Server Error (Broken Site)",
            "issues": [
                Issue(
                    id="server_error",
                    category="HTTP",
                    severity="high",
                    evidence="Status code 500 at https://example.com",
                    recommended_fix="Inspect server logs for stack traces"
                )
            ]
        },
        {
            "name": "SSL Certificate Expiring (Working but needs attention)",
            "issues": [
                Issue(
                    id="cert_expiring_soon",
                    category="TLS",
                    severity="medium",
                    evidence="Certificate expires in 5 day(s)",
                    recommended_fix="Renew your certificate"
                )
            ]
        },
        {
            "name": "Multiple Issues (DNS + Security Headers)",
            "issues": [
                Issue(
                    id="dns_a_lookup_error",
                    category="DNS",
                    severity="high",
                    evidence="A lookup error: NXDOMAIN",
                    recommended_fix="Verify domain exists"
                ),
                Issue(
                    id="security_headers_missing",
                    category="SecurityHeaders",
                    severity="low",
                    evidence="Missing: strict-transport-security, content-security-policy",
                    recommended_fix="Add recommended headers"
                )
            ]
        },
        {
            "name": "No Issues (Healthy Site)",
            "issues": []
        }
    ]
    
    for test_case in test_cases:
        print(f"\n[bold blue]Testing: {test_case['name']}[/bold blue]")
        print("=" * 60)
        
        result = convert_to_user_friendly(test_case['issues'])
        
        print(f"[bold]Is Broken:[/bold] {result.is_broken}")
        print(f"[bold]User Message:[/bold] {result.user_message}")
        
        if result.primary_issue:
            print(f"\n[bold]Primary Issue:[/bold]")
            print(f"  Title: {result.primary_issue.title}")
            print(f"  Description: {result.primary_issue.description}")
            print(f"  Impact: {result.primary_issue.impact}")
            print(f"  Solution: {result.primary_issue.solution}")
            print(f"  Urgency: {result.primary_issue.urgency}")
        
        if result.quick_fix:
            print(f"\n[bold]Quick Fix:[/bold] {result.quick_fix}")
        
        print(f"\n[bold]Total Issues:[/bold] {result.all_issues_count}")

if __name__ == "__main__":
    test_user_friendly_conversion()
