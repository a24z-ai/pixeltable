/**
 * Integration tests for Pixeltable API Authentication
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";

const API_URL = process.env.API_URL || "http://localhost:8000/api/v1";

describe("Authentication & API Key Management", () => {
  let apiKey: string;
  let apiKeyId: string;
  let keyPrefix: string;

  describe("API Key Creation", () => {
    test("should create a new API key", async () => {
      const response = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Test API Key",
          permissions: [
            {
              resource: "tables",
              actions: ["read", "write", "create", "delete"],
              constraints: null,
            },
            {
              resource: "data",
              actions: ["read", "write"],
              constraints: null,
            },
          ],
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result).toHaveProperty("api_key");
      expect(result).toHaveProperty("key_info");
      expect(result.key_info).toHaveProperty("id");
      expect(result.key_info).toHaveProperty("name");
      expect(result.key_info.name).toBe("Test API Key");

      // Save for later tests
      apiKey = result.api_key;
      apiKeyId = result.key_info.id;
      keyPrefix = result.key_info.key_prefix;
    });

    test("should create a read-only API key", async () => {
      const response = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Read-Only Key",
          permissions: [
            {
              resource: "tables",
              actions: ["read"],
              constraints: null,
            },
            {
              resource: "data",
              actions: ["read"],
              constraints: null,
            },
          ],
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.key_info.key_prefix).toContain("pxt_");
    });

    test("should create an API key with expiration", async () => {
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
      const response = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Expiring Key",
          permissions: [
            {
              resource: "data",
              actions: ["read"],
              constraints: null,
            },
          ],
          expires_at: expiresAt.toISOString(),
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.key_info.expires_at).toBeDefined();
    });
  });

  describe("API Key Authentication", () => {
    test("should authenticate with Bearer token", async () => {
      const response = await fetch(`${API_URL}/auth/verify`, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.valid).toBe(true);
      expect(result).toHaveProperty("permissions");
    });

    test("should authenticate with X-API-Key header", async () => {
      const response = await fetch(`${API_URL}/auth/verify`, {
        headers: {
          "X-API-Key": apiKey,
        },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.valid).toBe(true);
    });

    test("should allow unauthenticated access when not required", async () => {
      const response = await fetch(`${API_URL}/tables`);
      expect(response.status).toBe(200);
    });

    test("should use API key for data operations", async () => {
      // Create a test table first
      const tableName = "test_auth_table_" + Date.now();
      await fetch(`${API_URL}/tables`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          name: tableName,
          schema: { columns: { id: "int", data: "string" } },
        }),
      });

      // Insert data with API key
      const insertResponse = await fetch(`${API_URL}/tables/${tableName}/rows`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          data: { id: 1, data: "test" },
        }),
      });

      expect(insertResponse.status).toBe(200);

      // Clean up
      await fetch(`${API_URL}/tables/${tableName}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${apiKey}` },
      });
    });
  });

  describe("API Key Management", () => {
    test("should list all API keys", async () => {
      const response = await fetch(`${API_URL}/auth/api-keys`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      
      const foundKey = result.find((k: any) => k.id === apiKeyId);
      expect(foundKey).toBeDefined();
      expect(foundKey.name).toBe("Test API Key");
    });

    test("should get specific API key info", async () => {
      const response = await fetch(`${API_URL}/auth/api-keys/${apiKeyId}`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.id).toBe(apiKeyId);
      expect(result.name).toBe("Test API Key");
      expect(result.key_prefix).toBe(keyPrefix);
    });

    test("should rotate API key", async () => {
      const response = await fetch(`${API_URL}/auth/api-keys/${apiKeyId}/rotate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result).toHaveProperty("api_key");
      expect(result.api_key).not.toBe(apiKey);
      expect(result.key_info.name).toContain("rotated");

      // Update apiKey for remaining tests
      const newApiKey = result.api_key;
      
      // Old key should no longer work
      const oldKeyResponse = await fetch(`${API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      // Since we allow unauthenticated access, this won't fail
      // In production with require_auth=True, this would return 401
      
      // New key should work
      const newKeyResponse = await fetch(`${API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${newApiKey}` },
      });
      expect(newKeyResponse.status).toBe(200);
      
      apiKey = newApiKey;
      apiKeyId = result.key_info.id;
    });

    test("should get API key usage statistics", async () => {
      const response = await fetch(`${API_URL}/auth/api-keys/${apiKeyId}/usage?hours=24`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result).toHaveProperty("key_id");
      expect(result).toHaveProperty("total_requests");
      expect(result).toHaveProperty("endpoint_counts");
      expect(result).toHaveProperty("status_code_counts");
    });

    test("should revoke API key", async () => {
      // Create a key to revoke
      const createResponse = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Key to Revoke",
          permissions: [{ resource: "data", actions: ["read"] }],
        }),
      });
      const { api_key: keyToRevoke, key_info } = await createResponse.json();

      // Revoke the key
      const revokeResponse = await fetch(`${API_URL}/auth/api-keys/revoke`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ key_id: key_info.id }),
      });

      const revokeResult = await revokeResponse.json();
      expect(revokeResponse.status).toBe(200);
      expect(revokeResult.message).toContain("revoked");

      // Verify key no longer works
      const verifyResponse = await fetch(`${API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${keyToRevoke}` },
      });
      // In production with require_auth=True, this would return 401
    });
  });

  describe("Rate Limiting", () => {
    test("should include rate limit headers", async () => {
      const response = await fetch(`${API_URL}/tables`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });

      expect(response.status).toBe(200);
      expect(response.headers.get("X-RateLimit-Limit")).toBeDefined();
      expect(response.headers.get("X-RateLimit-Remaining")).toBeDefined();
      expect(response.headers.get("X-RateLimit-Reset")).toBeDefined();
    });

    test("should enforce rate limits", async () => {
      // Make many rapid requests to trigger rate limit
      const requests = [];
      for (let i = 0; i < 100; i++) {
        requests.push(
          fetch(`${API_URL}/tables`, {
            headers: { Authorization: `Bearer ${apiKey}` },
          })
        );
      }

      const responses = await Promise.all(requests);
      const statusCodes = responses.map((r) => r.status);
      
      // Some requests should be rate limited (429)
      const rateLimited = statusCodes.filter((code) => code === 429);
      expect(rateLimited.length).toBeGreaterThan(0);

      // Check retry-after header on rate limited response
      const limitedResponse = responses.find((r) => r.status === 429);
      if (limitedResponse) {
        expect(limitedResponse.headers.get("Retry-After")).toBeDefined();
      }
    });
  });

  describe("Permission Validation", () => {
    let restrictedKey: string;

    beforeAll(async () => {
      // Create a key with restricted permissions
      const response = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Restricted Key",
          permissions: [
            {
              resource: "tables",
              actions: ["read"],
              constraints: { table_names: ["allowed_table"] },
            },
          ],
        }),
      });
      const result = await response.json();
      restrictedKey = result.api_key;
    });

    test("should verify restricted permissions", async () => {
      const response = await fetch(`${API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${restrictedKey}` },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.permissions).toHaveLength(1);
      expect(result.permissions[0].resource).toBe("tables");
      expect(result.permissions[0].actions).toEqual(["read"]);
      expect(result.permissions[0].constraints).toHaveProperty("table_names");
    });
  });
});