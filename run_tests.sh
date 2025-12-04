#!/bin/bash

# Quick test runner script for Real Estate AI Platform
# Runs all tests with coverage and generates reports

set -e

echo "🧪 Running Real Estate AI Platform Test Suite..."
echo ""

# Check if we're in the backend directory or root
if [ -d "backend" ]; then
    TEST_DIR="backend"
else
    TEST_DIR="."
fi

# Change to backend directory
cd "$TEST_DIR" || exit 1

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing test dependencies..."
    pip install -r requirements.txt
fi

# Run tests with coverage
echo "🔍 Running tests with coverage..."
echo ""

# Run tests
pytest \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=term-missing \
    --verbose \
    --tb=short \
    tests/

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
    echo "   Open it with: open htmlcov/index.html (macOS) or start htmlcov/index.html (Windows)"
    echo ""
else
    echo ""
    echo "❌ Some tests failed. Check the output above for details."
    exit 1
fi

