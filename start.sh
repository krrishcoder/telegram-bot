#!/bin/bash

# Start script for the Telegram bot

echo "🚀 Starting Telegram Bot..."

# Detect if running in Render
if [ -n "$RENDER" ]; then
    echo "🟣 Running on Render — skipping .env check."
else
    # Local development: check for .env file
    if [ ! -f .env ]; then
        echo "❌ .env file not found!"
        echo "Please create a .env file based on .env.example"
        exit 1
    fi

    # Load .env file (only locally)
    export $(grep -v '^#' .env | xargs)
fi

# Check if virtual environment exists (for local use)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment (skip on Render)
if [ -z "$RENDER" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the bot
echo "🤖 Starting bot..."
python app.py
