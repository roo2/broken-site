#!/bin/bash

echo "🔧 Setting up Heroku buildpacks..."

# Get the app name from user
echo "📝 Enter your Heroku app name:"
read app_name

if [ -z "$app_name" ]; then
    echo "❌ App name is required"
    exit 1
fi

echo "🔗 Setting up buildpacks for app: $app_name"

# Clear existing buildpacks
echo "🧹 Clearing existing buildpacks..."
heroku buildpacks:clear --app "$app_name"

# Add Node.js buildpack first
echo "📦 Adding Node.js buildpack..."
heroku buildpacks:add heroku/nodejs --app "$app_name"

# Add Python buildpack second
echo "🐍 Adding Python buildpack..."
heroku buildpacks:add heroku/python --app "$app_name"

# Verify buildpacks
echo "✅ Verifying buildpacks..."
heroku buildpacks --app "$app_name"

echo "🎉 Buildpacks setup complete!"
echo "🚀 You can now deploy with: git push heroku main"
