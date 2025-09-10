#!/bin/bash
# Pre-commit hook for TypeScript SDK

set -e

echo "🔍 Running pre-commit checks for JS SDK..."

# Check if we're in the js-sdk directory or if js-sdk files are being committed
if [ -d "js-sdk" ]; then
    cd js-sdk
elif [ ! -f "package.json" ] || [ ! -d "src" ]; then
    # Not in js-sdk and no js-sdk changes
    exit 0
fi

# Check if any TypeScript/JavaScript files are being committed
if ! git diff --cached --name-only | grep -E '\.(ts|tsx|js|jsx)$' > /dev/null; then
    echo "No JS/TS files to check"
    exit 0
fi

echo "📝 Type checking..."
bun run typecheck

echo "🧪 Running tests..."
bun test

echo "✅ Pre-commit checks passed!"