#!/bin/bash
# Quick script to test API locally without Docker

set -e

echo "🚀 Starting Pixeltable API Integration Tests"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Check if API dependencies are installed
echo "📦 Checking dependencies..."
python -c "import fastapi" 2>/dev/null || {
    echo "Installing API dependencies..."
    uv pip install -e ".[api]"
}

# Start API server
echo "🔧 Starting API server..."
python -m pixeltable.api &
API_PID=$!

# Wait for server to be ready
echo "⏳ Waiting for server to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ API server is ready${NC}"
        break
    fi
    sleep 1
done

# Run JS SDK tests
echo "🧪 Running integration tests..."
cd js-sdk

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing JS SDK dependencies..."
    bun install
fi

# Run tests
if bun test ../tests/integration/api.test.ts; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Tests failed${NC}"
    exit 1
fi