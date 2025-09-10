/**
 * Integration tests for Pixeltable API
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";

// Import the SDK from the local js-sdk directory
import PixeltableClient from "../../js-sdk/src/index";

const API_URL = process.env.API_URL || "http://localhost:8000/api/v1";
const client = new PixeltableClient({ baseUrl: API_URL });

describe("Pixeltable API Integration Tests", () => {
  // Clean up test tables
  afterAll(async () => {
    const tables = await client.listTables();
    for (const table of tables) {
      if (table.startsWith("test_")) {
        await client.dropTable(table);
      }
    }
  });

  describe("Health Checks", () => {
    test("should return healthy status", async () => {
      const health = await client.health();
      expect(health.status).toBe("healthy");
    });
  });

  describe("Table Management", () => {
    const testTableName = "test_table_" + Date.now();

    test("should create a table", async () => {
      const result = await client.createTable(testTableName, {
        columns: {
          name: "string",
          age: "int",
          score: "float",
        },
      });
      expect(result.message).toContain("created successfully");
    });

    test("should list tables", async () => {
      const tables = await client.listTables();
      expect(tables).toContain(testTableName);
    });

    test("should get table info", async () => {
      const info = await client.getTable(testTableName);
      expect(info.name).toBe(testTableName);
      expect(info.column_count).toBe(3);
      expect(info.columns).toHaveLength(3);
    });

    test("should drop a table", async () => {
      const result = await client.dropTable(testTableName);
      expect(result.message).toContain("dropped successfully");
      
      // Verify it's gone
      const tables = await client.listTables();
      expect(tables).not.toContain(testTableName);
    });

    test("should handle errors for non-existent table", async () => {
      await expect(client.getTable("non_existent_table")).rejects.toThrow();
    });
  });

  describe("Data Types", () => {
    test("should support all basic data types", async () => {
      const tableName = "test_types_" + Date.now();
      
      const result = await client.createTable(tableName, {
        columns: {
          text_col: "string",
          int_col: "int",
          float_col: "float",
          bool_col: "bool",
          json_col: "json",
          timestamp_col: "timestamp",
        },
      });
      
      expect(result.message).toContain("created successfully");
      
      const info = await client.getTable(tableName);
      expect(info.columns).toHaveLength(6);
      
      // Clean up
      await client.dropTable(tableName);
    });
  });
});