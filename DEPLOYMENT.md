# BrokenSite Deployment Guide

## Quick Deploy

```bash
./deploy.sh
```

This script will:
1. Check Heroku CLI installation and login
2. Create or select a Heroku app
3. Set up environment variables
4. Configure buildpacks (Node.js + Python)
5. Deploy the application

## Manual Deploy

```bash
# Set up buildpacks
heroku buildpacks:clear --app YOUR_APP_NAME
heroku buildpacks:add heroku/nodejs --app YOUR_APP_NAME
heroku buildpacks:add heroku/python --app YOUR_APP_NAME

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key_here --app YOUR_APP_NAME

# Deploy
git push heroku main
```

## Local Development

```bash
# Start both backend and frontend
./start-dev.sh

# Or start individually
./start-backend.sh
./start-frontend.sh
```

## App Structure

- **Frontend**: React app in `/frontend/`
- **Backend**: FastAPI app in `/src/diagnostics/`
- **Build**: Heroku uses `heroku-build.sh` for deployment
- **Process**: Defined in `Procfile`
