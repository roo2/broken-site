#!/usr/bin/env python3
"""
Simple test script to verify the OpenAI agent functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from diagnostics.agent import run_agent_streaming
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
            print(f"[green]✓ Testing streaming agent[/green]")
            # Test the streaming agent
            updates = []
            for update in run_agent_streaming(target):
                updates.append(update)
                if update.get('type') == 'result':
                    print(f"[green]✓ Streaming completed[/green]")
                    break
                elif update.get('type') == 'error':
                    print(f"[red]✗ Streaming error: {update.get('message')}[/red]")
                    break
        except Exception as e:
            print(f"[red]✗ Error: {e}[/red]")

if __name__ == "__main__":
    test_agent()
