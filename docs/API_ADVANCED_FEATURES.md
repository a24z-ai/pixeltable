# Pixeltable API Advanced Features Documentation

## Overview

This document covers the advanced features of the Pixeltable API, including batch operations, asynchronous job processing, computed columns, user-defined functions (UDFs), webhooks, and data import/export capabilities.

## Batch Operations

Batch operations allow you to execute multiple data operations in a single request, improving performance and ensuring transactional consistency.

### Execute Batch Operations

**POST** `/api/v1/batch/operations`

Execute multiple insert, update, delete, or upsert operations in a batch.

**Request Body:**
```json
{
  "operations": [
    {
      "operation": "insert",
      "table": "products",
      "data": [
        {"id": 1, "name": "Product A", "price": 10.99},
        {"id": 2, "name": "Product B", "price": 20.99}
      ]
    },
    {
      "operation": "update",
      "table": "products",
      "where": {"id": 1},
      "set": {"price": 12.99}
    }
  ],
  "transaction": true,
  "continue_on_error": false,
  "return_results": true
}
```

**Response:**
```json
{
  "total_operations": 2,
  "successful": 2,
  "failed": 0,
  "errors": [],
  "results": [
    {"operation": 0, "status": "success"},
    {"operation": 1, "status": "success"}
  ],
  "execution_time_ms": 45.2
}
```

### Batch Operation Types

- **insert**: Add new rows to a table
- **update**: Modify existing rows based on conditions
- **delete**: Remove rows based on conditions  
- **upsert**: Insert or update based on existence

## Asynchronous Jobs

Long-running operations are executed as background jobs with progress tracking and status monitoring.

### Create Job

**POST** `/api/v1/batch/jobs`

Create an asynchronous job for data processing.

**Request Body:**
```json
{
  "job_type": "data_import",
  "parameters": {
    "table_name": "products",
    "format": "csv",
    "source_url": "https://example.com/data.csv"
  },
  "priority": 5,
  "webhook_url": "https://myapp.com/webhook",
  "webhook_events": ["completed", "failed"],
  "timeout_seconds": 3600
}
```

### Get Job Status

**GET** `/api/v1/batch/jobs/{job_id}`

Retrieve the current status and details of a job.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "data_import",
  "status": "running",
  "progress": 45.5,
  "parameters": {...},
  "result": null,
  "error": null,
  "created_at": "2024-01-15T10:00:00Z",
  "started_at": "2024-01-15T10:00:05Z",
  "logs": [
    "Job created",
    "Processing started",
    "Processed 1000 rows"
  ]
}
```

### Job Types

- **data_import**: Import data from external sources
- **data_export**: Export table data to various formats
- **batch_operation**: Execute batch operations
- **media_processing**: Process media files
- **table_recompute**: Recompute computed columns
- **custom**: Custom job types

### Job Status Values

- **pending**: Job queued for execution
- **running**: Job currently executing
- **completed**: Job finished successfully
- **failed**: Job encountered an error
- **cancelled**: Job was cancelled by user

## Computed Columns

Computed columns allow you to define derived values that are automatically calculated based on other column values.

### Create Computed Column

**POST** `/api/v1/tables/{table_name}/computed-columns`

Define a new computed column for a table.

**Request Body:**
```json
{
  "name": "total_value",
  "column_type": "expression",
  "expression": "price * quantity",
  "dependencies": ["price", "quantity"],
  "cache_results": true
}
```

### Column Types

- **expression**: Simple Python expressions
- **udf**: User-defined function
- **aggregate**: Aggregation functions (SUM, AVG, etc.)
- **window**: Window functions for analytics

### Recompute Column

**POST** `/api/v1/tables/{table_name}/computed-columns/{column_name}/recompute`

Trigger recomputation of a computed column.

```json
{
  "where": {"category": "electronics"}
}
```

## User-Defined Functions (UDFs)

Register custom functions that can be used in computed columns and queries.

### Register UDF

**POST** `/api/v1/tables/{table_name}/udfs`

Register a new user-defined function.

**Request Body:**
```json
{
  "name": "calculate_discount",
  "language": "python",
  "code": "def calculate_discount(price, discount_rate):\n    return price * (1 - discount_rate)",
  "parameters": [
    {"name": "price", "type": "float"},
    {"name": "discount_rate", "type": "float"}
  ],
  "return_type": "float",
  "description": "Calculate discounted price",
  "deterministic": true
}
```

### Supported Languages

- **python**: Python functions
- **sql**: SQL expressions
- **javascript**: JavaScript functions

### Execute UDF

**POST** `/api/v1/tables/{table_name}/udfs/{udf_name}/execute`

Test execute a UDF with parameters.

```json
{
  "price": 100.0,
  "discount_rate": 0.2
}
```

## Data Import/Export

Import data from various sources and export table data to different formats.

### Import Data

**POST** `/api/v1/batch/import`

Create an import job to load data into a table.

**Request Body:**
```json
{
  "table_name": "products",
  "format": "csv",
  "source_url": "https://example.com/products.csv",
  "mapping": {
    "product_id": "id",
    "product_name": "name",
    "product_price": "price"
  },
  "validation_rules": {
    "price": {"min": 0, "max": 10000}
  },
  "on_error": "skip",
  "batch_size": 1000
}
```

### Export Data

**POST** `/api/v1/batch/export`

Create an export job to extract table data.

**Request Body:**
```json
{
  "table_name": "products",
  "format": "json",
  "columns": ["id", "name", "price"],
  "where": {"category": "electronics"},
  "order_by": [{"column": "price", "direction": "desc"}],
  "limit": 1000,
  "compress": true
}
```

### Supported Formats

**Import Formats:**
- CSV
- JSON/JSONL
- Parquet
- Excel

**Export Formats:**
- CSV
- JSON/JSONL
- Parquet
- Excel
- Lance (Pixeltable native)

## Webhooks

Configure webhooks to receive real-time notifications about events.

### Register Webhook

**POST** `/api/v1/batch/webhooks`

Register a new webhook endpoint.

**Request Body:**
```json
{
  "url": "https://myapp.com/webhook",
  "events": [
    "job.completed",
    "job.failed",
    "table.updated",
    "data.inserted"
  ],
  "active": true,
  "secret": "webhook_secret_key",
  "headers": {
    "X-Custom-Header": "value"
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay_seconds": 60
  }
}
```

### Webhook Events

- **Job Events**: `job.started`, `job.progress`, `job.completed`, `job.failed`
- **Table Events**: `table.created`, `table.updated`, `table.deleted`
- **Data Events**: `data.inserted`, `data.updated`, `data.deleted`
- **Media Events**: `media.uploaded`, `media.processed`

### Webhook Payload

```json
{
  "webhook_id": "wh_123",
  "event": "job.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job_456",
    "result": {...}
  },
  "signature": "sha256=..."
}
```

## Data Streaming

Stream large datasets with chunking and compression support.

### Stream Data

**POST** `/api/v1/batch/stream/{table_name}`

Start streaming table data.

**Request Body:**
```json
{
  "chunk_size": 1000,
  "format": "jsonl",
  "compression": "gzip",
  "include_headers": true
}
```

**Response:** Streaming response with chunked data

### Stream Formats

- **json**: JSON array format
- **jsonl**: Newline-delimited JSON
- **csv**: Comma-separated values

## SDK Usage Examples

### JavaScript/TypeScript

```typescript
import PixeltableClient from '@a24z/pixeltable-sdk';

const client = new PixeltableClient({
  baseUrl: 'http://localhost:8000/api/v1',
  apiKey: 'YOUR_API_KEY'
});

// Batch operations
const batchResult = await client.executeBatchOperations({
  operations: [
    {
      operation: 'insert',
      table: 'products',
      data: [
        {id: 1, name: 'Product A', price: 10.99},
        {id: 2, name: 'Product B', price: 20.99}
      ]
    },
    {
      operation: 'update',
      table: 'products',
      where: {id: 1},
      set: {price: 12.99}
    }
  ],
  transaction: true
});

// Create async job
const job = await client.createJob({
  job_type: 'data_import',
  parameters: {
    table_name: 'products',
    format: 'csv',
    source_url: 'https://example.com/data.csv'
  }
});

// Monitor job progress
const status = await client.getJob(job.job_id);
console.log(`Job progress: ${status.progress}%`);

// Create computed column
const column = await client.createComputedColumn('products', {
  name: 'total_value',
  column_type: 'expression',
  expression: 'price * quantity',
  dependencies: ['price', 'quantity'],
  cache_results: true
});

// Register UDF
const udf = await client.registerUDF('products', {
  name: 'apply_discount',
  language: 'python',
  code: 'def apply_discount(price, rate): return price * (1 - rate)',
  parameters: [
    {name: 'price', type: 'float'},
    {name: 'rate', type: 'float'}
  ],
  return_type: 'float'
});

// Import data
const importJob = await client.importData({
  table_name: 'products',
  format: 'csv',
  source_url: 'https://example.com/products.csv',
  on_error: 'skip'
});

// Export data
const exportJob = await client.exportData({
  table_name: 'products',
  format: 'json',
  columns: ['id', 'name', 'price'],
  compress: true
});

// Register webhook
const webhook = await client.registerWebhook({
  url: 'https://myapp.com/webhook',
  events: ['job.completed', 'job.failed'],
  active: true
});

// Stream data
const stream = await client.streamData('products', {
  chunk_size: 1000,
  format: 'jsonl'
});
```

## Performance Considerations

1. **Batch Size**: Optimal batch size is typically 100-1000 operations
2. **Transaction Mode**: Use transactions for data consistency, disable for better performance
3. **Async Jobs**: Use for operations taking longer than 30 seconds
4. **Webhooks**: Implement idempotent webhook handlers
5. **Streaming**: Use for datasets larger than 10MB
6. **Computed Columns**: Cache results for expensive computations
7. **UDFs**: Mark deterministic functions for optimization

## Error Handling

Common error codes:

- **400**: Invalid request parameters or operation
- **403**: Insufficient permissions
- **404**: Resource not found
- **409**: Conflict (e.g., duplicate UDF name)
- **413**: Batch size exceeded
- **429**: Rate limit exceeded
- **500**: Internal server error

## Rate Limits

Advanced operations have specific rate limits:

- Batch operations: 100 requests per minute
- Job creation: 50 jobs per hour
- Webhook registration: 10 webhooks per API key
- Data streaming: 10 concurrent streams

## Best Practices

1. **Use Batch Operations**: Combine multiple operations for better performance
2. **Monitor Jobs**: Implement job status polling or use webhooks
3. **Validate Data**: Use validation rules during import
4. **Cache Computed Columns**: Enable caching for expensive computations
5. **Implement Retries**: Handle transient failures with exponential backoff
6. **Compress Exports**: Enable compression for large data exports
7. **Clean Up Jobs**: Periodically clean up completed job records
8. **Test UDFs**: Thoroughly test UDFs before using in production