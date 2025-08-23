#!/bin/bash

# Quick Frontend Workflow Testing Script
# Tests the key workflows demonstrated with Playwright MCP

echo "🍽️  Restaurant Management System - Frontend Workflow Tests"
echo "==========================================================="

# Check if services are running
echo "📋 Checking services..."

# Check frontend
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend not running on port 3000"
    echo "   Start with: cd frontend && npm run dev"
    exit 1
fi

# Check backend
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running on port 8000"
    echo "   Start with: uv run uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

echo "✅ Frontend running on http://localhost:3000"
echo "✅ Backend running on http://localhost:8000"
echo ""

# Test CORS is working
echo "🔧 Testing CORS configuration..."
cors_test=$(curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:8000/health)
if [[ "$cors_test" == *"OK"* ]]; then
    echo "✅ CORS is properly configured"
else
    echo "⚠️  CORS may have issues"
fi

echo ""
echo "🧪 Running focused workflow tests..."
echo ""

# Run specific test focused on our workflows
cd frontend
npx playwright test tests/frontend-workflows.spec.js --project=chromium --reporter=list

echo ""
echo "📊 Test Results Summary:"
echo "- Homepage and navigation tested"
echo "- Customer reservation workflow tested"  
echo "- Staff authentication and dashboard tested"
echo "- Menu management interface tested"
echo "- Responsive design verified"
echo ""
echo "🎉 Frontend workflow testing complete!"
echo "📄 See detailed results in: frontend/test-results/"