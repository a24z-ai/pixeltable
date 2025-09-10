# Pixeltable API & JS SDK - Milestone 1

## Overview
This milestone establishes the foundation for exposing Pixeltable via REST API and JavaScript SDK.

## What's Included

### 1. FastAPI Server (`pixeltable/api/`)
- Basic REST API server with table management endpoints
- Located within the main pixeltable package as an optional module
- Endpoints:
  - `GET /health` - Health check
  - `GET /ready` - Readiness check
  - `GET /api/v1/tables` - List all tables
  - `POST /api/v1/tables` - Create a new table
  - `GET /api/v1/tables/{name}` - Get table info
  - `DELETE /api/v1/tables/{name}` - Drop a table

### 2. JavaScript/TypeScript SDK (`js-sdk/`)
- TypeScript client library using Bun
- Type-safe API client with auto-generated types from OpenAPI schema
- Basic table management operations

## Setup Instructions

### Python API Server

1. Install with API dependencies:
```bash
# Using uv (project's package manager)
uv pip install -e ".[api]"

# Or using pip
pip install -e ".[api]"
```

2. Start the API server:
```bash
python -m pixeltable.api
```

The server will run at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

### JavaScript SDK

1. Install Bun (if not already installed):
```bash
curl -fsSL https://bun.sh/install | bash
```

2. Install dependencies:
```bash
cd js-sdk
bun install
```

3. Generate TypeScript types from API (server must be running):
```bash
bun run generate-types
```

4. Build the SDK:
```bash
bun run build
```

## Usage Examples

### Python API Server
```python
# The server initializes Pixeltable automatically
# Just run: python -m pixeltable.api
```

### JavaScript SDK
```typescript
import PixeltableClient from '@pixeltable/sdk';

const client = new PixeltableClient({
  baseUrl: 'http://localhost:8000/api/v1'
});

// Check health
const health = await client.health();

// List tables
const tables = await client.listTables();

// Create a table
await client.createTable('my_table', {
  columns: {
    name: 'string',
    age: 'int',
    score: 'float'
  }
});

// Get table info
const info = await client.getTable('my_table');

// Drop table
await client.dropTable('my_table');
```

## Architecture Decisions

1. **Monorepo Approach**: Both API and SDK start within the main pixeltable repo for easier development and iteration
2. **Optional Installation**: API server is an optional dependency (`pip install pixeltable[api]`)
3. **Type Generation**: TypeScript types are auto-generated from FastAPI's OpenAPI schema to ensure consistency
4. **Package Manager**: Using `uv` for Python (already in use) and `bun` for TypeScript/JavaScript

## Next Steps

- Add data insertion/query endpoints
- Add authentication/authorization
- Add streaming/websocket support for long operations
- Add more complex query capabilities
- Extract to separate packages when stable

## Testing

### API Server
```bash
# Run the server
python -m pixeltable.api

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/tables
```

### SDK
```bash
cd js-sdk
bun test
```