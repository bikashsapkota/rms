#!/bin/bash

# Database seeding script

echo "🌱 Restaurant Management System - Database Seeder"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Run migrations first
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Seed the database
echo "🌱 Seeding database with sample data..."
uv run python data/seeders/seed_data.py

echo ""
echo "✅ Database seeding completed!"
echo ""
echo "Demo users created (matching frontend):"
echo "  • manager@demorestaurant.com (password: password123)"
echo "  • staff@demorestaurant.com (password: password123)"
echo ""
echo "Additional sample users:"
echo "  • admin@pizzapalace.com (password: admin123!)"
echo "  • manager.downtown@pizzapalace.com (password: manager123!)"  
echo "  • staff.downtown@pizzapalace.com (password: staff123!)"
echo ""
echo "You can now start the API server with: ./scripts/start.sh"