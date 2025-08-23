#!/usr/bin/env python3
"""
Simple test script to verify the offline diagnosis functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from diagnostics.offline import run_offline_diagnosis
from rich import print

def test_offline_diagnosis():
    """Test the offline diagnosis with a known good domain"""
    test_targets = [
        "https://example.com",
        "https://httpbin.org",
        "google.com"  # Test without protocol
    ]
    
    for target in test_targets:
        print(f"\n[bold blue]Testing: {target}[/bold blue]")
        try:
            result = run_offline_diagnosis(target)
            print(f"[green]✓ Success[/green]")
            print(f"Summary: {result.summary}")
            print(f"Issues found: {len(result.issues)}")
            for issue in result.issues:
                print(f"  - [{issue.severity.upper()}] {issue.category}: {issue.evidence}")
        except Exception as e:
            print(f"[red]✗ Error: {e}[/red]")

if __name__ == "__main__":
    test_offline_diagnosis()
