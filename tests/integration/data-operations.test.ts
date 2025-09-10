/**
 * Integration tests for Pixeltable Data Operations API
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";

// Import the SDK from the local js-sdk directory
import PixeltableClient from "../../js-sdk/src/index";

const API_URL = process.env.API_URL || "http://localhost:8000/api/v1";
const client = new PixeltableClient({ baseUrl: API_URL });

describe("Data Operations Integration Tests", () => {
  const testTableName = "test_data_ops_" + Date.now();

  beforeAll(async () => {
    // Create test table
    await client.createTable(testTableName, {
      columns: {
        id: "int",
        name: "string",
        email: "string",
        age: "int",
        score: "float",
        active: "bool",
        metadata: "json",
        created_at: "timestamp",
      },
    });
  });

  afterAll(async () => {
    // Clean up test table
    await client.dropTable(testTableName);
  });

  describe("Data Insertion", () => {
    test("should insert a single row", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: {
            id: 1,
            name: "John Doe",
            email: "john@example.com",
            age: 30,
            score: 95.5,
            active: true,
            metadata: { role: "admin" },
            created_at: new Date().toISOString(),
          },
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.message).toContain("inserted successfully");
    });

    test("should insert multiple rows in batch", async () => {
      const rows = [
        {
          id: 2,
          name: "Jane Smith",
          email: "jane@example.com",
          age: 28,
          score: 88.0,
          active: true,
          metadata: { role: "user" },
          created_at: new Date().toISOString(),
        },
        {
          id: 3,
          name: "Bob Johnson",
          email: "bob@example.com",
          age: 35,
          score: 92.3,
          active: false,
          metadata: { role: "user" },
          created_at: new Date().toISOString(),
        },
      ];

      const response = await fetch(`${API_URL}/tables/${testTableName}/rows/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rows }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.row_count).toBe(2);
    });
  });

  describe("Data Querying", () => {
    test("should query all rows", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows`);
      const result = await response.json();

      expect(response.status).toBe(200);
      expect(result.rows).toBeInstanceOf(Array);
      expect(result.rows.length).toBeGreaterThanOrEqual(3);
    });

    test("should query with limit and offset", async () => {
      const response = await fetch(
        `${API_URL}/tables/${testTableName}/rows?limit=2&offset=1`
      );
      const result = await response.json();

      expect(response.status).toBe(200);
      expect(result.rows.length).toBeLessThanOrEqual(2);
      expect(result.has_more).toBeDefined();
    });

    test("should query specific columns", async () => {
      const response = await fetch(
        `${API_URL}/tables/${testTableName}/rows?select=name,email,age`
      );
      const result = await response.json();

      expect(response.status).toBe(200);
      if (result.rows.length > 0) {
        const firstRow = result.rows[0];
        expect(firstRow).toHaveProperty("name");
        expect(firstRow).toHaveProperty("email");
        expect(firstRow).toHaveProperty("age");
      }
    });

    test("should query with advanced filtering", async () => {
      const queryRequest = {
        select: ["name", "email", "age"],
        where: [
          { column: "age", operator: ">=", value: 25 },
          { column: "active", operator: "=", value: true },
        ],
        order_by: [{ column: "age", direction: "desc" }],
        limit: 10,
        offset: 0,
      };

      const response = await fetch(`${API_URL}/tables/${testTableName}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(queryRequest),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.rows).toBeInstanceOf(Array);
    });

    test("should handle like operator", async () => {
      const queryRequest = {
        where: [{ column: "name", operator: "like", value: "%John%" }],
      };

      const response = await fetch(`${API_URL}/tables/${testTableName}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(queryRequest),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.rows).toBeInstanceOf(Array);
    });

    test("should handle in operator", async () => {
      const queryRequest = {
        where: [{ column: "age", operator: "in", value: [28, 30, 35] }],
      };

      const response = await fetch(`${API_URL}/tables/${testTableName}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(queryRequest),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.rows).toBeInstanceOf(Array);
    });
  });

  describe("Data Updates", () => {
    test("should update multiple rows with where clause", async () => {
      const updateRequest = {
        where: [{ column: "active", operator: "=", value: false }],
        set: { active: true, score: 100.0 },
      };

      const response = await fetch(`${API_URL}/tables/${testTableName}/rows`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updateRequest),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.message).toContain("updated successfully");
    });

    test("should handle update by ID (when supported)", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows/1`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          row_id: "1",
          data: { score: 99.9 },
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      // Currently returns a message about not being implemented
      expect(result).toHaveProperty("message");
    });
  });

  describe("Data Deletion", () => {
    test("should delete rows with where clause", async () => {
      // First insert a row to delete
      await fetch(`${API_URL}/tables/${testTableName}/rows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: {
            id: 999,
            name: "To Delete",
            email: "delete@example.com",
            age: 99,
            score: 0,
            active: false,
            metadata: {},
            created_at: new Date().toISOString(),
          },
        }),
      });

      // Delete the row
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          where: [{ column: "id", operator: "=", value: 999 }],
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.message).toContain("deleted successfully");
    });

    test("should handle delete by ID (when supported)", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows/999`, {
        method: "DELETE",
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      // Currently returns a message about not being implemented
      expect(result).toHaveProperty("message");
    });
  });

  describe("Row Count", () => {
    test("should get row count", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows/count`);
      const result = await response.json();

      expect(response.status).toBe(200);
      expect(result).toHaveProperty("row_count");
      expect(typeof result.row_count).toBe("number");
    });
  });

  describe("Error Handling", () => {
    test("should handle invalid table name", async () => {
      const response = await fetch(`${API_URL}/tables/non_existent_table/rows`);
      expect(response.status).toBe(400);
    });

    test("should handle invalid column in where clause", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          where: [{ column: "invalid_column", operator: "=", value: 123 }],
        }),
      });

      expect(response.status).toBe(400);
    });

    test("should validate request body", async () => {
      const response = await fetch(`${API_URL}/tables/${testTableName}/rows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}), // Missing required 'data' field
      });

      expect(response.status).toBe(422);
    });
  });
});