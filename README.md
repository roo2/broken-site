# BrokenSite

An AI-powered website diagnostics tool that checks DNS, TLS/SSL, HTTP response chains, and common security headers. Features:
- **FastAPI backend** with real-time streaming diagnostics
- **OpenAI Responses API** agent with tool-calling and structured output
- **Modern React frontend** with real-time updates and markdown rendering
- **Offline mode** for running checks directly (no LLM) for local testing
- **Heroku deployment** ready with automatic buildpacks

## 🚀 Quick Start

### Option 1: Deploy to Heroku (Recommended)

```bash
# 1) Clone and deploy
git clone <your-repo>
cd vibecamp-broken-site
./deploy.sh

# 2) Set your OpenAI API key
heroku config:set OPENAI_API_KEY=your_key_here --app your-app-name

# 3) Open your app
heroku open --app your-app-name
```

### Option 2: Local Development

#### Backend Setup

```bash
# 1) Create a virtual environment and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Configure environment
cp env.example .env
# Set OPENAI_API_KEY, optionally change OPENAI_MODEL
# Set LOG_LEVEL=INFO for detailed logging during development

# 3) Run the API
./start-backend.sh
# or: uvicorn src.diagnostics.main:app --reload
# open http://localhost:8000/docs
```

#### Frontend Setup

```bash
# 1) Install frontend dependencies
cd frontend
npm install

# 2) Start the development server
npm run dev
# open http://localhost:3000
```

#### Full Stack Development

```bash
# Start both backend and frontend
./start-dev.sh
```

### Example API calls

```bash
# AI-powered diagnosis (default)
curl -X POST http://localhost:8000/api/diagnose/textual \
  -H "Content-Type: application/json" \
  -d '{"target":"https://example.com"}'

# Real-time streaming diagnosis
curl -X POST http://localhost:8000/api/diagnose/stream \
  -H "Content-Type: application/json" \
  -d '{"target":"https://example.com"}'

# Fast offline diagnosis
curl -X POST "http://localhost:8000/api/diagnose/textual?mode=offline" \
  -H "Content-Type: application/json" \
  -d '{"target":"https://example.com"}'
```

## 📁 Project Structure

```
vibecamp-broken-site/
├── src/diagnostics/          # Backend Python code
│   ├── main.py              # FastAPI app & routes
│   ├── config.py            # Settings via pydantic + dotenv
│   ├── schemas.py           # Pydantic models: inputs & structured report
│   ├── agent.py             # OpenAI Responses API agent (tool-calling)
│   ├── offline.py           # Deterministic, no-LLM diagnosis path
│   ├── user_friendly.py     # User-friendly report conversion
│   └── tools/               # Diagnostic tools
│       ├── dns_tools.py     # DNS resolution checks
│       ├── tls_tools.py     # TLS/SSL certificate validation
│       ├── http_tools.py    # HTTP response analysis
│       ├── hosting_tools.py # Hosting provider detection
│       └── screenshot_tools.py # Website screenshots
├── frontend/                # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.scss        # Component styles
│   │   └── styles/
│   │       └── main.scss   # Global styles
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── docs/                   # 📚 Detailed documentation
├── tests/                  # Test files
├── deploy.sh               # Heroku deployment script
├── heroku-build.sh         # Heroku build process
├── app.json                # Heroku configuration
├── Procfile                # Heroku process definition
├── requirements.txt        # Python dependencies
├── package.json            # Root package.json
├── runtime.txt             # Python version
├── .npmrc                  # NPM configuration
├── env.example             # Environment variables template
└── README.md              # This file
```

## 🛠️ Development

### Backend Development

- **Start backend**: `./start-backend.sh` or `uvicorn src.diagnostics.main:app --reload`
- **API documentation**: `http://localhost:8000/docs`
- **Health check**: `http://localhost:8000/healthz`

### Frontend Development

- **Start frontend**: `./start-frontend.sh` or `cd frontend && npm run dev`
- **Build for production**: `cd frontend && npm run build`
- **Preview build**: `cd frontend && npm run preview`

### Full Stack Development

- **Start both**: `./start-dev.sh` (starts backend on port 8000, frontend on port 3000)
- **Access frontend**: `http://localhost:3000`
- **API docs**: `http://localhost:8000/docs`

### Testing

```bash
# Run backend tests
python -m pytest tests/

# Test specific components
python tests/test_agent.py
python tests/test_offline.py
python tests/test_user_friendly.py
```

## ✨ Features

- **Real-time Streaming**: Watch the AI agent analyze websites in real-time with live updates
- **AI-Powered Analysis**: Uses OpenAI's Responses API with tool-calling for intelligent diagnostics
- **User-Friendly Reports**: Converts technical findings into simple, actionable recommendations
- **Hosting Detection**: Automatically detects hosting providers and provides specific guidance
- **Screenshot Capture**: Takes screenshots of websites to verify visual issues
- **Offline Mode**: Fast deterministic checks without AI for quick diagnostics
- **Modern UI**: React frontend with real-time markdown rendering and responsive design

## 🔧 Technical Details

- **Backend**: FastAPI with Server-Sent Events for real-time streaming
- **Frontend**: React with Vite, SCSS, and real-time markdown rendering
- **AI Integration**: OpenAI Responses API with structured tool-calling
- **Deployment**: Heroku-ready with automatic Node.js and Python buildpacks
- **Testing**: Comprehensive test suite for all components

## 📚 Documentation

For detailed documentation, see the [docs/](./docs/) folder:
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Project Brief](./docs/project-brief.md)
- [Development History](./docs/README.md)

## 🚀 Deployment

The app is production-ready and deployed on Heroku. See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed deployment instructions.
