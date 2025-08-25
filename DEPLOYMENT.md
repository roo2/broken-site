# Heroku Deployment Guide

This guide will help you deploy the BrokenSite application to Heroku.

## Prerequisites

1. **Heroku CLI** installed and logged in
2. **Git** repository with your code
3. **OpenAI API Key** for AI-powered diagnostics

## Deployment Steps

### 1. Install Heroku CLI (if not already installed)
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create a new Heroku app
```bash
heroku create your-app-name
```

### 4. Set up environment variables
```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
heroku config:set LOG_LEVEL=INFO
```

### 5. Deploy to Heroku
```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### 6. Open your app
```bash
heroku open
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI-powered diagnostics)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - defaults to INFO

### Buildpacks
The app uses two buildpacks:
1. **Node.js buildpack**: For building the React frontend
2. **Python buildpack**: For running the FastAPI backend

## Troubleshooting

### Common Issues

1. **Build fails**: Check the build logs with `heroku logs --tail`
2. **Playwright issues**: The build script installs Chromium browser for Playwright
3. **Frontend not loading**: Ensure the frontend/dist directory is being served correctly

### View Logs
```bash
heroku logs --tail
```

### Restart the app
```bash
heroku restart
```

## Local Development

To test the deployment locally:
```bash
# Build the frontend
cd frontend
npm install
npm run build
cd ..

# Run the backend
uvicorn src.diagnostics.main:app --reload
```

## Notes

- The app uses Playwright for screenshot functionality, which requires browser installation
- The frontend is built during deployment and served as static files
- The FastAPI backend serves both the API endpoints and the frontend static files
