# @a24z/pixeltable-sdk

Official JavaScript/TypeScript SDK for Pixeltable API.

## Installation

```bash
npm install @a24z/pixeltable-sdk
# or
yarn add @a24z/pixeltable-sdk
# or
bun add @a24z/pixeltable-sdk
```

## Quick Start

```typescript
import PixeltableClient from '@a24z/pixeltable-sdk';

const client = new PixeltableClient({
  baseUrl: 'http://localhost:8000/api/v1', // Optional, this is the default
  apiKey: 'your-api-key' // Optional, for authentication when implemented
});

// Check API health
const health = await client.health();
console.log(health); // { status: 'healthy' }

// List all tables
const tables = await client.listTables();
console.log(tables); // ['table1', 'table2', ...]

// Create a new table
await client.createTable('my_table', {
  columns: {
    id: 'int',
    name: 'string',
    score: 'float',
    is_active: 'bool'
  }
});

// Get table information
const tableInfo = await client.getTable('my_table');
console.log(tableInfo);
// {
//   name: 'my_table',
//   column_count: 4,
//   columns: [
//     { name: 'id', type: 'int', is_computed: false },
//     { name: 'name', type: 'string', is_computed: false },
//     ...
//   ]
// }

// Drop a table
await client.dropTable('my_table');
```

## Data Operations (New in v0.2.0)

```typescript
// Insert data
await client.insertRow('my_table', {
  id: 1,
  name: 'John Doe',
  score: 95.5,
  is_active: true
});

await client.insertRows('my_table', {
  rows: [
    { id: 2, name: 'Jane', score: 88.0 },
    { id: 3, name: 'Bob', score: 92.3 }
  ]
});

// Query data
const results = await client.query('my_table', {
  select: ['name', 'score'],
  where: [
    { column: 'score', operator: '>=', value: 90 },
    { column: 'is_active', operator: '=', value: true }
  ],
  order_by: [{ column: 'score', direction: 'desc' }],
  limit: 10
});

// Update data
await client.updateRows('my_table', {
  where: [{ column: 'score', operator: '<', value: 60 }],
  set: { is_active: false }
});

// Delete data
await client.deleteRows('my_table', {
  where: [{ column: 'is_active', operator: '=', value: false }]
});

// Count rows
const count = await client.countRows('my_table');
console.log(`Total rows: ${count.row_count}`);
```

## API Reference

### `new PixeltableClient(config?)`

Creates a new Pixeltable client instance.

#### Parameters
- `config.baseUrl` (string, optional): The base URL of the Pixeltable API. Defaults to `http://localhost:8000/api/v1`
- `config.apiKey` (string, optional): API key for authentication (when implemented)

### `client.health()`

Returns the health status of the API server.

### `client.listTables()`

Returns an array of table names.

### `client.createTable(name, schema)`

Creates a new table with the specified schema.

#### Parameters
- `name` (string): The name of the table to create
- `schema.columns` (object): Column definitions mapping column names to types

#### Supported Types
- `string`: Text data
- `int`: Integer numbers
- `float`: Floating-point numbers
- `bool`: Boolean values
- `json`: JSON objects
- `timestamp`: Date/time values
- `image`: Image data
- `video`: Video data
- `audio`: Audio data
- `document`: Document data

### `client.getTable(name)`

Retrieves information about a specific table.

#### Parameters
- `name` (string): The name of the table

### `client.dropTable(name)`

Deletes a table.

#### Parameters
- `name` (string): The name of the table to delete

### Data Operations

#### `client.insertRow(tableName, data)`

Inserts a single row into a table.

#### `client.insertRows(tableName, request)`

Inserts multiple rows into a table.

#### `client.query(tableName, request)`

Performs an advanced query with filtering, sorting, and pagination.

##### Query Parameters
- `select`: Array of column names to return
- `where`: Array of filter conditions
- `order_by`: Array of sort specifications
- `limit`: Maximum rows to return
- `offset`: Number of rows to skip

##### Where Clause Operators
- `=`, `!=`, `>`, `>=`, `<`, `<=`: Comparison operators
- `like`: Pattern matching (use % for wildcards)
- `in`, `not_in`: List membership
- `is_null`, `is_not_null`: Null checks

#### `client.updateRows(tableName, request)`

Updates rows matching the specified conditions.

#### `client.deleteRows(tableName, request)`

Deletes rows matching the specified conditions.

#### `client.countRows(tableName)`

Returns the count of rows in a table.

## TypeScript Support

This SDK is written in TypeScript and provides full type definitions out of the box.

```typescript
import PixeltableClient, { TableSchema, TableInfo } from '@a24z/pixeltable-sdk';

const schema: TableSchema = {
  columns: {
    id: 'int',
    name: 'string'
  }
};

const info: TableInfo = await client.getTable('my_table');
```

## Requirements

- Node.js >= 18.0.0
- Pixeltable API server running (see [main repository](https://github.com/a24z-ai/pixeltable))

## Development

```bash
# Install dependencies
bun install

# Run tests
bun test

# Type check
bun run typecheck

# Build
bun run build

# Generate types from API
bun run generate-types
```

## License

Apache-2.0

## Contributing

See the [main repository](https://github.com/a24z-ai/pixeltable) for contribution guidelines.