#!/bin/bash

# Test runner script

echo "🧪 Running Restaurant Management System Tests"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync --dev

# Set test environment
export DATABASE_URL="postgresql+asyncpg://rms_user:rms_pass@localhost:5433/rms_test"
export TEST_DATABASE_URL="postgresql+asyncpg://rms_user:rms_pass@localhost:5433/rms_test"

# Run specific test type or all tests
case "${1:-all}" in
    "unit")
        echo "🔬 Running unit tests..."
        uv run pytest tests/unit/ -v
        ;;
    "integration") 
        echo "🔗 Running integration tests..."
        uv run pytest tests/integration/ -v
        ;;
    "coverage")
        echo "📊 Running tests with coverage report..."
        uv run pytest --cov=app --cov-report=html --cov-report=term-missing
        echo "   Coverage report generated in htmlcov/index.html"
        ;;
    "all"|*)
        echo "🚀 Running all tests..."
        uv run pytest -v
        ;;
esac

echo ""
echo "✅ Test run completed!"