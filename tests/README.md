# Test Scripts

This directory contains test scripts for the BrokenSite application.

## Test Sites

Heroku 500 error the-story-generator.com
Wordpress 500 error in plugin sizzling-tasman.51-161-218-147.id-host.com 
Wordpress 200 but error in div blank-sven.51-161-218-147.id-host.com
expired domain realprofits.com
expired certificate https://chat.therapyboard.com.au/


Other tests todo:
cloudflare is down ?
DNS Misconfigured
expired hosting
upbeat-tasman.51-161-218-147.id-host.com





### Core Functionality Tests

- **`test_app_import.py`** - Tests that the FastAPI app can be imported correctly
- **`test_offline.py`** - Tests the offline diagnosis functionality
- **`test_agent.py`** - Tests the OpenAI agent functionality (requires API key)

### OpenAI Integration Tests

- **`test_openai_fix.py`** - Validates OpenAI tool format and configuration
- **`test_openai_api.py`** - Tests the complete OpenAI API integration

### User Experience Tests

- **`test_user_friendly.py`** - Tests the user-friendly conversion logic
- **`test_api_modes.py`** - Tests both offline and OpenAI modes of the API

### Utility Tests

- **`test_logging.py`** - Tests logging configuration and functionality

## Running Tests

### From Command Line

```bash
# Test OpenAI tools format
python tests/test_openai_fix.py

# Test OpenAI API integration
python tests/test_openai_api.py

# Test offline diagnosis
python tests/test_offline.py

# Test app import
python tests/test_app_import.py
```

### From VS Code

Use the debug configurations in `.vscode/launch.json`:

- **Test Offline Diagnosis** - Tests offline mode
- **Test Agent** - Tests OpenAI agent (requires API key)
- **Test User-Friendly Conversion** - Tests conversion logic
- **Test API Modes** - Tests both modes
- **Test OpenAI Tools** - Validates tool format
- **Test OpenAI API** - Tests complete API integration

## Prerequisites

- Python virtual environment activated
- OpenAI API key set in `.env` file (for OpenAI tests)
- All dependencies installed (`pip install -r requirements.txt`)

## Test Coverage

These tests cover:
- ✅ Tool format validation
- ✅ Function calling logic
- ✅ JSON response parsing
- ✅ Schema validation
- ✅ User-friendly conversion
- ✅ API endpoint functionality
- ✅ Error handling
- ✅ Logging configuration
