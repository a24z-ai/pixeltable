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

export interface TableInfo {
  name: string;
  column_count: number;
  columns: Array<{
    name: string;
    type: string;
    is_computed: boolean;
  }>;
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
}

export default PixeltableClient;