/**
 * Pixeltable JavaScript SDK
 */

export interface PixeltableConfig {
  baseUrl?: string;
  apiKey?: string;
}

export interface TableSchema {
  columns: Record<string, string>;
}

export interface ColumnInfo {
  name: string;
  type: string;
  is_computed: boolean;
  nullable?: boolean;
}

export interface TableInfo {
  name: string;
  column_count: number;
  row_count?: number;
  columns: ColumnInfo[];
  created_at?: string;
}

export interface WhereClause {
  column: string;
  operator: '=' | '!=' | '>' | '>=' | '<' | '<=' | 'like' | 'in' | 'not_in' | 'is_null' | 'is_not_null';
  value?: any;
}

export interface OrderByClause {
  column: string;
  direction: 'asc' | 'desc';
}

export interface QueryRequest {
  select?: string[];
  where?: WhereClause[];
  order_by?: OrderByClause[];
  limit?: number;
  offset?: number;
}

export interface QueryResponse {
  rows: Record<string, any>[];
  total_count?: number;
  has_more: boolean;
  next_offset?: number;
}

export interface InsertRowsRequest {
  rows: Record<string, any>[];
  batch_size?: number;
}

export interface UpdateRowsRequest {
  where: WhereClause[];
  set: Record<string, any>;
}

export interface DeleteRowsRequest {
  where?: WhereClause[];
  soft_delete?: boolean;
}

export interface Permission {
  resource: 'tables' | 'data' | 'media' | 'admin';
  actions: Array<'read' | 'write' | 'delete' | 'create'>;
  constraints?: Record<string, any>;
}

export interface CreateAPIKeyRequest {
  name: string;
  permissions: Permission[];
  expires_at?: string;
}

export interface APIKeyInfo {
  id: string;
  name: string;
  key_prefix: string;
  permissions: Permission[];
  created_at: string;
  last_used?: string;
  expires_at?: string;
  revoked: boolean;
}

export interface APIKeyResponse {
  api_key: string;
  key_info: APIKeyInfo;
}

export interface APIUsageStats {
  key_id: string;
  endpoint_counts: Record<string, number>;
  status_code_counts: Record<number, number>;
  total_requests: number;
  avg_response_time_ms: number;
  period_start: string;
  period_end: string;
}

export type MediaType = 'image' | 'video' | 'audio' | 'document' | 'other';
export type MediaFormat = 'jpeg' | 'png' | 'gif' | 'webp' | 'svg' | 'mp4' | 'webm' | 'avi' | 'mov' | 
                          'mp3' | 'wav' | 'ogg' | 'aac' | 'pdf' | 'txt' | 'doc' | 'docx' | 'xls' | 'xlsx' | 
                          'csv' | 'json' | 'xml' | 'html' | 'md' | 'other';
export type ProcessingOperation = 'thumbnail' | 'resize' | 'convert' | 'compress' | 'extract_metadata' | 
                                  'extract_text' | 'extract_audio' | 'extract_frames' | 'transcode';
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export interface MediaMetadata {
  width?: number;
  height?: number;
  duration?: number;
  frame_rate?: number;
  bit_rate?: number;
  sample_rate?: number;
  channels?: number;
  codec?: string;
  [key: string]: any;
}

export interface MediaInfo {
  media_id: string;
  filename: string;
  media_type: MediaType;
  format: MediaFormat;
  size_bytes: number;
  url: string;
  storage_path: string;
  storage_backend: string;
  metadata: MediaMetadata;
  table_name?: string;
  column_name?: string;
  row_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface MediaUploadOptions {
  metadata?: Record<string, any>;
  table_name?: string;
  column_name?: string;
  row_id?: string;
}

export interface MediaURLIngestionRequest {
  url: string;
  filename?: string;
  metadata?: Record<string, any>;
  table_name?: string;
  column_name?: string;
  row_id?: string;
}

export interface MediaProcessingRequest {
  operation: ProcessingOperation;
  parameters?: Record<string, any>;
  output_format?: MediaFormat;
  webhook_url?: string;
}

export interface ProcessingJob {
  job_id: string;
  media_id: string;
  operation: ProcessingOperation;
  parameters?: Record<string, any>;
  status: ProcessingStatus;
  progress?: number;
  result?: Record<string, any>;
  error?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface MediaSearchParams {
  query?: string;
  media_type?: MediaType;
  format?: MediaFormat;
  min_size?: number;
  max_size?: number;
  created_after?: string;
  created_before?: string;
  table_name?: string;
  column_name?: string;
  limit?: number;
  offset?: number;
}

// Advanced Features Types
export type ComputedColumnType = 'expression' | 'udf' | 'aggregate' | 'window';
export type UDFLanguage = 'python' | 'sql' | 'javascript';
export type BatchOperationType = 'insert' | 'update' | 'delete' | 'upsert';
export type JobType = 'data_import' | 'data_export' | 'batch_operation' | 'media_processing' | 'table_recompute' | 'custom';
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type ImportFormat = 'csv' | 'json' | 'jsonl' | 'parquet' | 'excel';
export type ExportFormat = 'csv' | 'json' | 'jsonl' | 'parquet' | 'excel' | 'lance';
export type WebhookEvent = 'job.started' | 'job.progress' | 'job.completed' | 'job.failed' | 
                          'table.created' | 'table.updated' | 'table.deleted' |
                          'data.inserted' | 'data.updated' | 'data.deleted' |
                          'media.uploaded' | 'media.processed';

export interface ComputedColumnDefinition {
  name: string;
  column_type: ComputedColumnType;
  expression: string;
  dependencies?: string[];
  parameters?: Record<string, any>;
  cache_results?: boolean;
}

export interface ComputedColumnInfo extends ComputedColumnDefinition {
  created_at: string;
  last_computed?: string;
  computation_time_ms?: number;
}

export interface UDFDefinition {
  name: string;
  language: UDFLanguage;
  code: string;
  parameters: Array<{ name: string; type: string }>;
  return_type: string;
  description?: string;
  deterministic?: boolean;
}

export interface UDFInfo {
  id: string;
  name: string;
  language: UDFLanguage;
  parameters: Array<{ name: string; type: string }>;
  return_type: string;
  description?: string;
  deterministic: boolean;
  created_at: string;
  updated_at?: string;
  usage_count: number;
}

export interface BatchOperation {
  operation: BatchOperationType;
  table: string;
  data?: any | any[];
  where?: Record<string, any>;
  set?: Record<string, any>;
}

export interface BatchRequest {
  operations: BatchOperation[];
  transaction?: boolean;
  continue_on_error?: boolean;
  return_results?: boolean;
}

export interface BatchResult {
  total_operations: number;
  successful: number;
  failed: number;
  errors: Array<Record<string, any>>;
  results?: any[];
  execution_time_ms: number;
}

export interface JobRequest {
  job_type: JobType;
  parameters: Record<string, any>;
  priority?: number;
  webhook_url?: string;
  webhook_events?: string[];
  timeout_seconds?: number;
}

export interface JobInfo {
  job_id: string;
  job_type: JobType;
  status: JobStatus;
  progress: number;
  parameters: Record<string, any>;
  result?: Record<string, any>;
  error?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  webhook_url?: string;
  logs: string[];
}

export interface ImportRequest {
  table_name: string;
  format: ImportFormat;
  source_url?: string;
  mapping?: Record<string, string>;
  options?: Record<string, any>;
  validation_rules?: Record<string, any>;
  on_error?: 'skip' | 'fail' | 'default';
  batch_size?: number;
}

export interface ExportRequest {
  table_name: string;
  format: ExportFormat;
  destination_url?: string;
  columns?: string[];
  where?: Record<string, any>;
  order_by?: Array<{ column: string; direction: 'asc' | 'desc' }>;
  limit?: number;
  options?: Record<string, any>;
  compress?: boolean;
}

export interface WebhookConfig {
  url: string;
  events: WebhookEvent[];
  active?: boolean;
  secret?: string;
  headers?: Record<string, string>;
  retry_config?: Record<string, any>;
}

export interface WebhookInfo {
  webhook_id: string;
  url: string;
  events: WebhookEvent[];
  active: boolean;
  created_at: string;
  last_triggered?: string;
  success_count: number;
  failure_count: number;
}

export interface StreamConfig {
  chunk_size?: number;
  format?: 'json' | 'jsonl' | 'csv';
  compression?: 'gzip' | 'brotli';
  include_headers?: boolean;
}

export class PixeltableClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: PixeltableConfig = {}) {
    this.baseUrl = config.baseUrl || 'http://localhost:8000/api/v1';
    this.headers = {
      'Content-Type': 'application/json',
    };
    if (config.apiKey) {
      this.headers['Authorization'] = `Bearer ${config.apiKey}`;
    }
  }

  async health(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`, {
      headers: this.headers,
    });
    return response.json() as Promise<{ status: string }>;
  }

  async listTables(): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/tables`, {
      headers: this.headers,
    });
    if (!response.ok) {
      throw new Error(`Failed to list tables: ${response.statusText}`);
    }
    return response.json() as Promise<string[]>;
  }

  async createTable(name: string, schema: TableSchema): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/tables`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ name, schema }),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to create table: ${error.detail}`);
    }
    return response.json() as Promise<{ message: string }>;
  }

  async getTable(name: string): Promise<TableInfo> {
    const response = await fetch(`${this.baseUrl}/tables/${name}`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to get table: ${error.detail}`);
    }
    return response.json() as Promise<TableInfo>;
  }

  async dropTable(name: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/tables/${name}`, {
      method: 'DELETE',
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to drop table: ${error.detail}`);
    }
    return response.json() as Promise<{ message: string }>;
  }

  // Data Operations

  async insertRow(tableName: string, data: Record<string, any>): Promise<{ message: string; data: Record<string, any> }> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ data }),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to insert row: ${error.detail}`);
    }
    return response.json();
  }

  async insertRows(tableName: string, request: InsertRowsRequest): Promise<{ message: string; row_count: number }> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows/batch`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to insert rows: ${error.detail}`);
    }
    return response.json();
  }

  async queryRows(tableName: string, options?: {
    select?: string;
    limit?: number;
    offset?: number;
  }): Promise<QueryResponse> {
    const params = new URLSearchParams();
    if (options?.select) params.append('select', options.select);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());

    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows?${params}`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to query rows: ${error.detail}`);
    }
    return response.json();
  }

  async query(tableName: string, request: QueryRequest): Promise<QueryResponse> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/query`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to query: ${error.detail}`);
    }
    return response.json();
  }

  async updateRow(tableName: string, rowId: string | number, data: Record<string, any>): Promise<any> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows/${rowId}`, {
      method: 'PUT',
      headers: this.headers,
      body: JSON.stringify({ row_id: rowId, data }),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to update row: ${error.detail}`);
    }
    return response.json();
  }

  async updateRows(tableName: string, request: UpdateRowsRequest): Promise<{ message: string; updated_fields: string[] }> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows`, {
      method: 'PATCH',
      headers: this.headers,
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to update rows: ${error.detail}`);
    }
    return response.json();
  }

  async deleteRow(tableName: string, rowId: string | number): Promise<any> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows/${rowId}`, {
      method: 'DELETE',
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to delete row: ${error.detail}`);
    }
    return response.json();
  }

  async deleteRows(tableName: string, request: DeleteRowsRequest): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows`, {
      method: 'DELETE',
      headers: this.headers,
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to delete rows: ${error.detail}`);
    }
    return response.json();
  }

  async countRows(tableName: string): Promise<{ table_name: string; row_count: number }> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/rows/count`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to count rows: ${error.detail}`);
    }
    return response.json();
  }

  // Authentication Operations

  async createAPIKey(request: CreateAPIKeyRequest): Promise<APIKeyResponse> {
    const response = await fetch(`${this.baseUrl}/auth/api-keys`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to create API key: ${error.detail}`);
    }
    return response.json();
  }

  async listAPIKeys(): Promise<APIKeyInfo[]> {
    const response = await fetch(`${this.baseUrl}/auth/api-keys`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to list API keys: ${error.detail}`);
    }
    return response.json();
  }

  async getAPIKey(keyId: string): Promise<APIKeyInfo> {
    const response = await fetch(`${this.baseUrl}/auth/api-keys/${keyId}`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to get API key: ${error.detail}`);
    }
    return response.json();
  }

  async revokeAPIKey(keyId?: string, keyPrefix?: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/auth/api-keys/revoke`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ key_id: keyId, key_prefix: keyPrefix }),
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to revoke API key: ${error.detail}`);
    }
    return response.json();
  }

  async rotateAPIKey(keyId: string): Promise<APIKeyResponse> {
    const response = await fetch(`${this.baseUrl}/auth/api-keys/${keyId}/rotate`, {
      method: 'POST',
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to rotate API key: ${error.detail}`);
    }
    return response.json();
  }

  async getAPIKeyUsage(keyId: string, hours: number = 24): Promise<APIUsageStats> {
    const response = await fetch(`${this.baseUrl}/auth/api-keys/${keyId}/usage?hours=${hours}`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to get API key usage: ${error.detail}`);
    }
    return response.json();
  }

  async verifyAuth(): Promise<{
    valid: boolean;
    api_key_id?: string;
    permissions?: Permission[];
    rate_limit?: Record<string, any>;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/verify`, {
      headers: this.headers,
    });
    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to verify auth: ${error.detail}`);
    }
    return response.json();
  }

  // Media Operations

  async uploadMedia(file: File, options?: MediaUploadOptions): Promise<MediaInfo> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options?.metadata) {
      formData.append('metadata', JSON.stringify(options.metadata));
    }
    if (options?.table_name) {
      formData.append('table_name', options.table_name);
    }
    if (options?.column_name) {
      formData.append('column_name', options.column_name);
    }
    if (options?.row_id) {
      formData.append('row_id', options.row_id);
    }

    const headers = { ...this.headers };
    delete headers['Content-Type']; // Let browser set multipart boundary

    const response = await fetch(`${this.baseUrl}/media/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to upload media: ${error.detail}`);
    }
    return response.json();
  }

  async ingestMediaFromURL(request: MediaURLIngestionRequest): Promise<MediaInfo> {
    const response = await fetch(`${this.baseUrl}/media/ingest`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to ingest media from URL: ${error.detail}`);
    }
    return response.json();
  }

  async getMedia(mediaId: string): Promise<MediaInfo> {
    const response = await fetch(`${this.baseUrl}/media/${mediaId}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to get media: ${error.detail}`);
    }
    return response.json();
  }

  async downloadMedia(mediaId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/media/${mediaId}/download`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to download media: ${error.detail}`);
    }
    return response.blob();
  }

  async deleteMedia(mediaId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/media/${mediaId}`, {
      method: 'DELETE',
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to delete media: ${error.detail}`);
    }
    return response.json();
  }

  async searchMedia(params?: MediaSearchParams): Promise<MediaInfo[]> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }

    const url = queryParams.toString() 
      ? `${this.baseUrl}/media/search?${queryParams}`
      : `${this.baseUrl}/media/search`;

    const response = await fetch(url, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to search media: ${error.detail}`);
    }
    return response.json();
  }

  async processMedia(mediaId: string, request: MediaProcessingRequest): Promise<ProcessingJob> {
    const response = await fetch(`${this.baseUrl}/media/${mediaId}/process`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to process media: ${error.detail}`);
    }
    return response.json();
  }

  async getProcessingJob(jobId: string): Promise<ProcessingJob> {
    const response = await fetch(`${this.baseUrl}/media/jobs/${jobId}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to get processing job: ${error.detail}`);
    }
    return response.json();
  }

  async cancelProcessingJob(jobId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/media/jobs/${jobId}/cancel`, {
      method: 'POST',
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to cancel processing job: ${error.detail}`);
    }
    return response.json();
  }

  async listProcessingJobs(mediaId?: string, status?: ProcessingStatus): Promise<ProcessingJob[]> {
    const queryParams = new URLSearchParams();
    if (mediaId) queryParams.append('media_id', mediaId);
    if (status) queryParams.append('status', status);

    const url = queryParams.toString()
      ? `${this.baseUrl}/media/jobs?${queryParams}`
      : `${this.baseUrl}/media/jobs`;

    const response = await fetch(url, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to list processing jobs: ${error.detail}`);
    }
    return response.json();
  }

  // Advanced Features Operations

  async executeBatchOperations(request: BatchRequest): Promise<BatchResult> {
    const response = await fetch(`${this.baseUrl}/batch/operations`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to execute batch operations: ${error.detail}`);
    }
    return response.json();
  }

  async createJob(request: JobRequest): Promise<JobInfo> {
    const response = await fetch(`${this.baseUrl}/batch/jobs`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to create job: ${error.detail}`);
    }
    return response.json();
  }

  async getJob(jobId: string): Promise<JobInfo> {
    const response = await fetch(`${this.baseUrl}/batch/jobs/${jobId}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to get job: ${error.detail}`);
    }
    return response.json();
  }

  async listJobs(status?: JobStatus, jobType?: JobType, limit: number = 50): Promise<JobInfo[]> {
    const queryParams = new URLSearchParams();
    if (status) queryParams.append('status', status);
    if (jobType) queryParams.append('job_type', jobType);
    queryParams.append('limit', limit.toString());

    const response = await fetch(`${this.baseUrl}/batch/jobs?${queryParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to list jobs: ${error.detail}`);
    }
    return response.json();
  }

  async cancelJob(jobId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/batch/jobs/${jobId}/cancel`, {
      method: 'POST',
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to cancel job: ${error.detail}`);
    }
    return response.json();
  }

  async importData(request: ImportRequest): Promise<JobInfo> {
    const response = await fetch(`${this.baseUrl}/batch/import`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to import data: ${error.detail}`);
    }
    return response.json();
  }

  async exportData(request: ExportRequest): Promise<JobInfo> {
    const response = await fetch(`${this.baseUrl}/batch/export`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to export data: ${error.detail}`);
    }
    return response.json();
  }

  async createComputedColumn(tableName: string, column: ComputedColumnDefinition): Promise<ComputedColumnInfo> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/computed-columns`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(column),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to create computed column: ${error.detail}`);
    }
    return response.json();
  }

  async listComputedColumns(tableName: string): Promise<ComputedColumnInfo[]> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/computed-columns`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to list computed columns: ${error.detail}`);
    }
    return response.json();
  }

  async deleteComputedColumn(tableName: string, columnName: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/computed-columns/${columnName}`, {
      method: 'DELETE',
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to delete computed column: ${error.detail}`);
    }
    return response.json();
  }

  async registerUDF(tableName: string, udf: UDFDefinition): Promise<UDFInfo> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/udfs`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(udf),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to register UDF: ${error.detail}`);
    }
    return response.json();
  }

  async listUDFs(tableName: string): Promise<UDFInfo[]> {
    const response = await fetch(`${this.baseUrl}/tables/${tableName}/udfs`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to list UDFs: ${error.detail}`);
    }
    return response.json();
  }

  async registerWebhook(config: WebhookConfig): Promise<WebhookInfo> {
    const response = await fetch(`${this.baseUrl}/batch/webhooks`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to register webhook: ${error.detail}`);
    }
    return response.json();
  }

  async listWebhooks(): Promise<WebhookInfo[]> {
    const response = await fetch(`${this.baseUrl}/batch/webhooks`, {
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to list webhooks: ${error.detail}`);
    }
    return response.json();
  }

  async deleteWebhook(webhookId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/batch/webhooks/${webhookId}`, {
      method: 'DELETE',
      headers: this.headers,
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to delete webhook: ${error.detail}`);
    }
    return response.json();
  }

  async streamData(tableName: string, config: StreamConfig, where?: WhereClause[]): Promise<ReadableStream> {
    const response = await fetch(`${this.baseUrl}/batch/stream/${tableName}`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ ...config, where }),
    });

    if (!response.ok) {
      const error = await response.json() as { detail: string };
      throw new Error(`Failed to stream data: ${error.detail}`);
    }

    if (!response.body) {
      throw new Error('No response body for streaming');
    }

    return response.body;
  }
}

export default PixeltableClient;