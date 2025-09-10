#!/bin/bash
# Generate TypeScript types from FastAPI OpenAPI schema

echo "Starting FastAPI server to generate OpenAPI schema..."

# Start the server in background
python -m pixeltable.api &
SERVER_PID=$!

# Wait for server to be ready
sleep 3

# Download OpenAPI schema
curl -s http://localhost:8000/openapi.json > openapi.json

# Kill the server
kill $SERVER_PID

# Generate TypeScript types using openapi-typescript
echo "Generating TypeScript types..."
cd js-sdk
npx openapi-typescript ../openapi.json -o src/generated/api-types.ts

# Clean up
cd ..
rm openapi.json

echo "TypeScript types generated successfully!"