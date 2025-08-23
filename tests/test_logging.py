#!/usr/bin/env python3
"""
Test script to verify logging configuration
"""
import sys
import os
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logging_configuration():
    """Test different logging levels"""
    
    print("🧪 Testing Logging Configuration")
    print("=" * 50)
    
    # Test default logging (ERROR only)
    print("\n📋 Testing Default Logging (ERROR only)...")
    
    # Import the main module to trigger logging setup
    from diagnostics.main import logger
    
    print("✅ Logger configured successfully")
    print(f"   Current log level: {logging.getLevelName(logger.level)}")
    
    # Test different log levels
    test_levels = [
        ("ERROR", "ERROR"),
        ("WARNING", "WARNING"), 
        ("INFO", "INFO"),
        ("DEBUG", "DEBUG")
    ]
    
    print("\n🔍 Testing Log Level Environment Variable...")
    for env_level, expected_level in test_levels:
        # Temporarily set environment variable
        original_level = os.environ.get("LOG_LEVEL")
        os.environ["LOG_LEVEL"] = env_level
        
        # Re-import to test new level
        try:
            # Clear existing loggers
            logging.getLogger().handlers.clear()
            
            # Re-import main to trigger new logging setup
            import importlib
            import diagnostics.main
            importlib.reload(diagnostics.main)
            
            logger = diagnostics.main.logger
            actual_level = logging.getLevelName(logger.level)
            
            if actual_level == expected_level:
                print(f"✅ LOG_LEVEL={env_level} → {actual_level}")
            else:
                print(f"❌ LOG_LEVEL={env_level} → {actual_level} (expected {expected_level})")
                
        except Exception as e:
            print(f"❌ Error testing LOG_LEVEL={env_level}: {e}")
        finally:
            # Restore original environment
            if original_level:
                os.environ["LOG_LEVEL"] = original_level
            else:
                os.environ.pop("LOG_LEVEL", None)
    
    print("\n🎯 Logging Configuration Summary:")
    print("- Default: ERROR level (minimal output)")
    print("- Set LOG_LEVEL=INFO in .env for detailed logs")
    print("- Set LOG_LEVEL=DEBUG for maximum verbosity")
    print("- Available levels: ERROR, WARNING, INFO, DEBUG")

if __name__ == "__main__":
    test_logging_configuration()
