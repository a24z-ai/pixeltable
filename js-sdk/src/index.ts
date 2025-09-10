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
}

export default PixeltableClient;