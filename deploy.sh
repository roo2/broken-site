#!/bin/bash

# Heroku Deployment Script for BrokenSite

echo "🚀 Starting Heroku deployment for BrokenSite..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run 'heroku login' first."
    exit 1
fi

# Get app name from user
echo "📝 Enter your Heroku app name (or press Enter to create a new one):"
read app_name

if [ -z "$app_name" ]; then
    echo "🆕 Creating new Heroku app..."
    app_name=$(heroku create --json | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
    echo "✅ Created app: $app_name"
else
    echo "🔗 Using existing app: $app_name"
fi

# Check if app exists
if ! heroku apps:info --app "$app_name" &> /dev/null; then
    echo "❌ App '$app_name' does not exist. Please create it first or check the name."
    exit 1
fi

# Set up environment variables
echo "🔧 Setting up environment variables..."

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable is not set."
    echo "   Please set it with: export OPENAI_API_KEY=your_key_here"
    echo "   Or set it in Heroku with: heroku config:set OPENAI_API_KEY=your_key_here"
    echo ""
    echo "   Continue anyway? (y/n):"
    read continue_deploy
    if [ "$continue_deploy" != "y" ]; then
        echo "❌ Deployment cancelled."
        exit 1
    fi
else
    echo "✅ Setting OPENAI_API_KEY..."
    heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" --app "$app_name"
fi

# Set other environment variables
echo "✅ Setting LOG_LEVEL..."
heroku config:set LOG_LEVEL=INFO --app "$app_name"

# Set up buildpacks
echo "🔧 Setting up buildpacks..."
echo "🧹 Clearing existing buildpacks..."
heroku buildpacks:clear --app "$app_name"

echo "📦 Adding Node.js buildpack..."
heroku buildpacks:add heroku/nodejs --app "$app_name"

echo "🐍 Adding Python buildpack..."
heroku buildpacks:add heroku/python --app "$app_name"

echo "✅ Verifying buildpacks..."
heroku buildpacks --app "$app_name"

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku - $(date)"

echo "📤 Pushing to Heroku..."
git push heroku main

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Opening your app..."
    heroku open --app "$app_name"
    
    echo ""
    echo "🎉 Your BrokenSite app is now live!"
    echo "🔗 URL: https://$app_name.herokuapp.com"
    echo ""
    echo "📊 View logs: heroku logs --tail --app $app_name"
    echo "🔄 Restart app: heroku restart --app $app_name"
else
    echo "❌ Deployment failed. Check the logs above for errors."
    echo "📊 View logs: heroku logs --tail --app $app_name"
    exit 1
fi
