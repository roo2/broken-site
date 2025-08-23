# Debugging Guide

This guide explains how to debug the Site Diagnostics Pro project using VS Code or Cursor.

## Launch Configurations

The project includes several debug configurations in `.vscode/launch.json`:

### 1. FastAPI Debug
- **Name**: "FastAPI Debug"
- **Purpose**: Debug the FastAPI application using uvicorn module
- **Use case**: When you want to debug the main application logic (recommended)

### 2. FastAPI Debug (Uvicorn)
- **Name**: "FastAPI Debug (Uvicorn)"
- **Purpose**: Debug using uvicorn server
- **Use case**: Alternative debugging method (same as FastAPI Debug)

### 3. Test Offline Diagnosis
- **Name**: "Test Offline Diagnosis"
- **Purpose**: Test the offline diagnosis functionality
- **Use case**: Debug the diagnostic tools without OpenAI integration

### 4. Test Agent
- **Name**: "Test Agent"
- **Purpose**: Test the OpenAI agent functionality
- **Use case**: Debug the AI-powered diagnosis (requires OPENAI_API_KEY)

### 5. Test User-Friendly Conversion
- **Name**: "Test User-Friendly Conversion"
- **Purpose**: Test the user-friendly issue conversion
- **Use case**: Debug the non-technical user interface logic

## How to Use

1. **Open the project in VS Code/Cursor**
2. **Set breakpoints** in your code where you want to pause execution
3. **Go to the Debug panel** (Ctrl+Shift+D / Cmd+Shift+D)
4. **Select a launch configuration** from the dropdown
5. **Click the green play button** or press F5

## Environment Setup

### For OpenAI Agent Testing
Create a `.env` file in the project root:
```bash
cp env.example .env
# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_api_key_here
```

### Python Interpreter
The launch configurations automatically use the virtual environment (`.venv`). If you need to change it:
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose `.venv/bin/python`

## Debugging Tips

### Setting Breakpoints
- Click in the left margin next to line numbers to set breakpoints
- Use conditional breakpoints for specific scenarios
- Use logpoints for non-intrusive debugging

### Debug Console
- Use the Debug Console to evaluate expressions
- Access variables in the current scope
- Test function calls

### Watch Variables
- Add variables to the Watch panel for continuous monitoring
- Use expressions like `len(result.issues)` to watch computed values

## Common Debug Scenarios

### 1. Debugging DNS Issues
Set breakpoints in `src/diagnostics/tools/dns_tools.py` and use "Test Offline Diagnosis"

### 2. Debugging HTTP Issues
Set breakpoints in `src/diagnostics/tools/http_tools.py` and use "Test Offline Diagnosis"

### 3. Debugging OpenAI Agent
Set breakpoints in `src/diagnostics/agent.py` and use "Test Agent"

### 4. Debugging API Endpoints
Set breakpoints in `src/diagnostics/main.py` and use "FastAPI Debug"

### 5. Debugging User-Friendly Conversion
Set breakpoints in `src/diagnostics/user_friendly.py` and use "Test User-Friendly Conversion"

## Testing the Setup

1. **Test offline functionality**:
   ```bash
   python test_offline.py
   ```

2. **Test the API server**:
   ```bash
   uvicorn diagnostics.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
3. **Test app import**:
   ```bash
   python test_app_import.py
   ```

3. **Test with curl**:
   ```bash
   curl -X POST http://localhost:8000/diagnose \
     -H "Content-Type: application/json" \
     -d '{"target":"https://example.com"}'
   ```

## Troubleshooting

### Import Errors
- Ensure `PYTHONPATH` includes the `src` directory
- Verify the virtual environment is activated
- Check that all dependencies are installed

### OpenAI API Errors
- Verify your API key is correct
- Check your OpenAI account has sufficient credits
- Ensure the model specified in config is available

### Network Issues
- Check firewall settings
- Verify DNS resolution works
- Test with different target URLs
