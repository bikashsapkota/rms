#!/bin/bash

# Start development server script

echo "🚀 Starting Restaurant Management System - Development Server"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    echo "   Please run: cd /path/to/rms && ./scripts/start.sh"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '#' | xargs)
else
    echo "⚠️  Warning: .env file not found. Using defaults."
    echo "   Copy .env.example to .env and configure as needed."
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Seed database if requested
if [ "$1" = "--seed" ]; then
    echo "🌱 Seeding database with sample data..."
    uv run python data/seeders/seed_data.py
fi

# Start the server
echo "🌐 Starting FastAPI development server..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop the server"
echo ""

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload