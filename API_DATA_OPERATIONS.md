# Pixeltable API Data Operations Documentation

## Overview
This document describes the data operations endpoints added in Milestone 2 of the Pixeltable API development.

## Base URL
```
http://localhost:8000/api/v1
```

## Data Operations Endpoints

### 1. Insert Operations

#### Insert Single Row
```http
POST /tables/{table_name}/rows
Content-Type: application/json

{
  "data": {
    "column1": "value1",
    "column2": 123,
    "column3": true
  }
}
```

**Response:**
```json
{
  "message": "Row inserted successfully",
  "data": { ... }
}
```

#### Insert Multiple Rows (Batch)
```http
POST /tables/{table_name}/rows/batch
Content-Type: application/json

{
  "rows": [
    {"column1": "value1", "column2": 123},
    {"column1": "value2", "column2": 456}
  ],
  "batch_size": 100  // optional
}
```

**Response:**
```json
{
  "message": "Successfully inserted 2 rows",
  "row_count": 2
}
```

### 2. Query Operations

#### Basic Query
```http
GET /tables/{table_name}/rows?select=col1,col2&limit=100&offset=0
```

**Response:**
```json
{
  "rows": [...],
  "has_more": true,
  "next_offset": 100
}
```

#### Advanced Query with Filtering
```http
POST /tables/{table_name}/query
Content-Type: application/json

{
  "select": ["name", "email", "age"],
  "where": [
    {"column": "age", "operator": ">=", "value": 18},
    {"column": "status", "operator": "=", "value": "active"}
  ],
  "order_by": [
    {"column": "created_at", "direction": "desc"}
  ],
  "limit": 50,
  "offset": 0
}
```

**Supported Where Operators:**
- `=` - Equals
- `!=` - Not equals
- `>` - Greater than
- `>=` - Greater than or equal
- `<` - Less than
- `<=` - Less than or equal
- `like` - Pattern matching (use % for wildcards)
- `in` - Value in list
- `not_in` - Value not in list
- `is_null` - Column is null
- `is_not_null` - Column is not null

**Response:**
```json
{
  "rows": [
    {"name": "John", "email": "john@example.com", "age": 25}
  ],
  "has_more": false,
  "next_offset": null
}
```

### 3. Update Operations

#### Update Single Row (Currently Limited)
```http
PUT /tables/{table_name}/rows/{row_id}
Content-Type: application/json

{
  "row_id": "123",
  "data": {
    "column1": "new_value",
    "column2": 999
  }
}
```

**Note:** Single row updates by ID are not yet fully supported in Pixeltable core.

#### Update Multiple Rows
```http
PATCH /tables/{table_name}/rows
Content-Type: application/json

{
  "where": [
    {"column": "status", "operator": "=", "value": "pending"}
  ],
  "set": {
    "status": "active",
    "updated_at": "2025-01-10T12:00:00Z"
  }
}
```

**Response:**
```json
{
  "message": "Rows updated successfully",
  "updated_fields": ["status", "updated_at"]
}
```

### 4. Delete Operations

#### Delete Single Row (Currently Limited)
```http
DELETE /tables/{table_name}/rows/{row_id}
```

**Note:** Single row deletion by ID is not yet fully supported in Pixeltable core.

#### Delete Multiple Rows
```http
DELETE /tables/{table_name}/rows
Content-Type: application/json

{
  "where": [
    {"column": "status", "operator": "=", "value": "archived"}
  ],
  "soft_delete": false
}
```

**Response:**
```json
{
  "message": "Rows deleted successfully",
  "soft_delete": false
}
```

### 5. Utility Operations

#### Count Rows
```http
GET /tables/{table_name}/rows/count
```

**Response:**
```json
{
  "table_name": "users",
  "row_count": 1234
}
```

## JavaScript/TypeScript SDK Usage

### Installation
```bash
npm install @pixeltable/sdk
# or
bun add @pixeltable/sdk
```

### Usage Examples

```typescript
import PixeltableClient from '@pixeltable/sdk';

const client = new PixeltableClient({
  baseUrl: 'http://localhost:8000/api/v1'
});

// Insert single row
await client.insertRow('users', {
  name: 'John Doe',
  email: 'john@example.com',
  age: 30
});

// Insert multiple rows
await client.insertRows('users', {
  rows: [
    { name: 'Jane', email: 'jane@example.com' },
    { name: 'Bob', email: 'bob@example.com' }
  ]
});

// Query with filtering
const results = await client.query('users', {
  select: ['name', 'email'],
  where: [
    { column: 'age', operator: '>=', value: 18 }
  ],
  order_by: [
    { column: 'name', direction: 'asc' }
  ],
  limit: 100
});

// Update rows
await client.updateRows('users', {
  where: [
    { column: 'status', operator: '=', value: 'inactive' }
  ],
  set: {
    status: 'active',
    updated_at: new Date().toISOString()
  }
});

// Delete rows
await client.deleteRows('users', {
  where: [
    { column: 'deleted', operator: '=', value: true }
  ]
});

// Count rows
const count = await client.countRows('users');
console.log(`Total users: ${count.row_count}`);
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters, table not found, etc.)
- `422` - Unprocessable Entity (validation errors)
- `500` - Internal Server Error

Error Response Format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Current Limitations

1. **Row-level operations by ID**: Direct update/delete by row ID is not yet supported by Pixeltable core. Use where clauses instead.

2. **Pagination**: Offset-based pagination is currently implemented by fetching all results and slicing, which is inefficient for large datasets.

3. **Count operations**: Row counting requires fetching all rows, which is inefficient for large tables.

4. **Transactions**: Multi-operation transactions are not yet supported.

## Testing

Integration tests are available in `tests/integration/data-operations.test.ts`.

Run tests with Docker:
```bash
docker-compose -f docker-compose.test.yml up --build
```

## Next Steps

- Media handling endpoints
- Authentication and API key management
- Computed columns API
- Performance optimizations for pagination and counting
- Transaction support