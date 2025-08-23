# BrokenSite (Python)

An initial project framework for an AI-powered website diagnostics assistant that checks DNS, TLS/SSL, HTTP response chains, and common security headers. Comes with:
- FastAPI service (`/diagnose` endpoint)
- Modular checkers (DNS, TLS, HTTP, security headers, email auth basics)
- Optional OpenAI **Responses API** agent with tool-calling and structured output
- Offline mode for running checks directly (no LLM) for local testing
- **Modern React frontend** with SCSS and Vite bundling

## Quick start

### Backend Setup

```bash
# 1) Create a virtual environment and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # or: pip install -e .

# 2) Configure env
cp env.example .env
# set OPENAI_API_KEY, optionally change OPENAI_MODEL
# set LOG_LEVEL=INFO for detailed logging during development

# 3) Run the API
uvicorn src.diagnostics.main:app --reload
# open http://localhost:8000/docs
```

### Frontend Setup

```bash
# 1) Install frontend dependencies
cd frontend
npm install

# 2) Start the development server
npm run dev
# open http://localhost:3000
```

### Example API call

```bash
# AI-powered diagnosis (default)
curl -X POST http://localhost:8000/diagnose/user-friendly \
  -H "Content-Type: application/json" \
  -d '{"target":"https://example.com"}'

# Fast offline diagnosis
curl -X POST "http://localhost:8000/diagnose/user-friendly?mode=offline" \
  -H "Content-Type: application/json" \
  -d '{"target":"https://example.com"}'
```

## Project layout

```
vibecamp-broken-site/
├── src/diagnostics/          # Backend Python code
│   ├── main.py              # FastAPI app & routes
│   ├── config.py            # Settings via pydantic + dotenv
│   ├── schemas.py           # Pydantic models: inputs & structured report
│   ├── agent.py             # OpenAI Responses API agent (tool-calling)
│   ├── offline.py           # Deterministic, no-LLM diagnosis path
│   └── tools/               # Diagnostic tools
│       ├── dns_tools.py
│       ├── tls_tools.py
│       ├── http_tools.py
│       └── security_tools.py
├── frontend/                # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.scss        # Component styles
│   │   └── styles/
│   │       └── main.scss   # Global styles
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── .vscode/                # VS Code debugging configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Development

### Backend Development

- **Debug with VS Code**: Use the launch configurations in `.vscode/launch.json`
- **Test offline mode**: `python test_offline.py`
- **Test agent mode**: `python test_agent.py` (requires OPENAI_API_KEY)
- **Test user-friendly conversion**: `python test_user_friendly.py`
- **Test API modes**: `python test_api_modes.py`

### Frontend Development

- **Development server**: `cd frontend && npm run dev`
- **Build for production**: `cd frontend && npm run build`
- **Preview build**: `cd frontend && npm run preview`

### Full Stack Development

1. **Start backend**: `uvicorn diagnostics.main:app --reload`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Access frontend**: `http://localhost:3000`
4. **API docs**: `http://localhost:8000/docs`

## Notes

- **Default Mode**: The app now uses **AI-powered diagnosis** by default for better analysis and recommendations
- **Fallback Mode**: If no OpenAI API key is set, users can switch to "Fast Check" mode for offline diagnostics
- **User-Friendly**: The frontend provides a simple toggle between AI-powered and fast offline modes
- The OpenAI agent uses **tool calling** and **structured outputs** to return a machine-readable report
- The frontend uses **Vite** for fast development and **SCSS** for modern styling
- Extend by adding more tools: traceroute, mixed-content scan, CDN detection, WHOIS registrar status analysis, etc.
- The TLS probe here retrieves the peer certificate and parses expiry. For full chain/OCSP and cipher details, wire in `openssl s_client`, `sslscan`, or libraries like `cryptography` with deeper parsing.
