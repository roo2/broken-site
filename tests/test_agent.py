#!/usr/bin/env python3
"""
Simple test script to verify the OpenAI agent functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from diagnostics.agent import run_agent
from diagnostics.config import settings
from rich import print

def test_agent():
    """Test the OpenAI agent with a known good domain"""
    if not settings.OPENAI_API_KEY:
        print("[red]✗ OPENAI_API_KEY not set. Please set it in your environment or .env file[/red]")
        return
    
    test_targets = [
        "https://example.com",
        "https://httpbin.org"
    ]
    
    for target in test_targets:
        print(f"\n[bold blue]Testing Agent: {target}[/bold blue]")
        try:
            result = run_agent(target)
            print(f"[green]✓ Success[/green]")
            print(f"Summary: {result.summary}")
            print(f"Issues found: {len(result.issues)}")
            for issue in result.issues:
                print(f"  - [{issue.severity.upper()}] {issue.category}: {issue.evidence}")
        except Exception as e:
            print(f"[red]✗ Error: {e}[/red]")

if __name__ == "__main__":
    test_agent()
