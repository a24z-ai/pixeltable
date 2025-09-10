/**
 * Integration tests for Pixeltable Media API
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";

const API_URL = process.env.API_URL || "http://localhost:8000/api/v1";

// Helper to create a test file
function createTestFile(content: string, filename: string, mimeType: string): File {
  const blob = new Blob([content], { type: mimeType });
  return new File([blob], filename, { type: mimeType });
}

describe("Media Operations", () => {
  let apiKey: string;
  let uploadedMediaId: string;
  let processingJobId: string;

  beforeAll(async () => {
    // Create an API key for testing
    const keyResponse = await fetch(`${API_URL}/auth/api-keys`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Media Test Key",
        permissions: [
          {
            resource: "media",
            actions: ["read", "write", "create", "delete"],
            constraints: null,
          },
        ],
      }),
    });
    const keyResult = await keyResponse.json();
    apiKey = keyResult.api_key;
  });

  describe("File Upload", () => {
    test("should upload an image file", async () => {
      const formData = new FormData();
      const testImage = createTestFile(
        "fake image content",
        "test-image.jpg",
        "image/jpeg"
      );
      formData.append("file", testImage);
      formData.append("metadata", JSON.stringify({ tags: ["test", "image"] }));

      const response = await fetch(`${API_URL}/media/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        body: formData,
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result).toHaveProperty("media_id");
      expect(result.filename).toBe("test-image.jpg");
      expect(result.media_type).toBe("image");
      expect(result.format).toBe("jpeg");
      expect(result).toHaveProperty("url");
      expect(result).toHaveProperty("storage_path");

      uploadedMediaId = result.media_id;
    });

    test("should upload with table/column reference", async () => {
      const formData = new FormData();
      const testDoc = createTestFile(
        "document content",
        "document.pdf",
        "application/pdf"
      );
      formData.append("file", testDoc);
      formData.append("table_name", "products");
      formData.append("column_name", "manual");
      formData.append("row_id", "123");

      const response = await fetch(`${API_URL}/media/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        body: formData,
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.media_type).toBe("document");
      expect(result.format).toBe("pdf");
      expect(result.metadata.table_name).toBe("products");
      expect(result.metadata.column_name).toBe("manual");
      expect(result.metadata.row_id).toBe("123");
    });

    test("should handle various file types", async () => {
      const testFiles = [
        { content: "video", name: "video.mp4", mime: "video/mp4", type: "video" },
        { content: "audio", name: "audio.mp3", mime: "audio/mpeg", type: "audio" },
        { content: "text", name: "doc.txt", mime: "text/plain", type: "document" },
      ];

      for (const testFile of testFiles) {
        const formData = new FormData();
        const file = createTestFile(testFile.content, testFile.name, testFile.mime);
        formData.append("file", file);

        const response = await fetch(`${API_URL}/media/upload`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${apiKey}`,
          },
          body: formData,
        });

        const result = await response.json();
        expect(response.status).toBe(200);
        expect(result.media_type).toBe(testFile.type);
        expect(result.filename).toBe(testFile.name);
      }
    });
  });

  describe("URL Ingestion", () => {
    test("should ingest media from URL", async () => {
      const response = await fetch(`${API_URL}/media/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          url: "https://via.placeholder.com/150",
          metadata: { source: "placeholder" },
        }),
      });

      if (response.ok) {
        const result = await response.json();
        expect(result).toHaveProperty("media_id");
        expect(result.media_type).toBe("image");
        expect(result.metadata.source_url).toBe("https://via.placeholder.com/150");
      }
      // Note: This might fail in test environment without internet access
    });
  });

  describe("Media Retrieval", () => {
    test("should get media info", async () => {
      const response = await fetch(`${API_URL}/media/${uploadedMediaId}`, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.media_id).toBe(uploadedMediaId);
      expect(result.filename).toBe("test-image.jpg");
      expect(result).toHaveProperty("size_bytes");
      expect(result).toHaveProperty("created_at");
    });

    test("should download media file", async () => {
      const response = await fetch(`${API_URL}/media/${uploadedMediaId}/download`, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      expect(response.status).toBe(200);
      expect(response.headers.get("content-disposition")).toContain("test-image.jpg");
    });

    test("should handle non-existent media", async () => {
      const fakeId = "550e8400-e29b-41d4-a716-446655440000";
      const response = await fetch(`${API_URL}/media/${fakeId}`, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      expect(response.status).toBe(404);
    });
  });

  describe("Media Processing", () => {
    test("should create processing job for thumbnail", async () => {
      const response = await fetch(`${API_URL}/media/${uploadedMediaId}/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          operation: "thumbnail",
          parameters: {
            width: 128,
            height: 128,
          },
        }),
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result).toHaveProperty("job_id");
      expect(result.media_id).toBe(uploadedMediaId);
      expect(result.operation).toBe("thumbnail");
      expect(result.status).toBeOneOf(["pending", "processing"]);

      processingJobId = result.job_id;
    });

    test("should get processing job status", async () => {
      if (!processingJobId) return;

      const response = await fetch(`${API_URL}/media/jobs/${processingJobId}`, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(result.job_id).toBe(processingJobId);
      expect(result).toHaveProperty("status");
      expect(result).toHaveProperty("progress");
    });

    test("should support various processing operations", async () => {
      const operations = [
        {
          operation: "resize",
          parameters: { width: 800, height: 600, maintain_aspect: true },
        },
        {
          operation: "convert",
          output_format: "webp",
        },
        {
          operation: "extract_metadata",
          parameters: {},
        },
      ];

      for (const op of operations) {
        const response = await fetch(`${API_URL}/media/${uploadedMediaId}/process`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify(op),
        });

        const result = await response.json();
        expect(response.status).toBe(200);
        expect(result.operation).toBe(op.operation);
      }
    });
  });

  describe("Media Search", () => {
    test("should search media files", async () => {
      const response = await fetch(
        `${API_URL}/media/search?media_type=image&limit=10`,
        {
          headers: {
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(Array.isArray(result)).toBe(true);
      if (result.length > 0) {
        expect(result[0]).toHaveProperty("media_id");
        expect(result[0].media_type).toBe("image");
      }
    });

    test("should search with query text", async () => {
      const response = await fetch(
        `${API_URL}/media/search?query=test&limit=5`,
        {
          headers: {
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(Array.isArray(result)).toBe(true);
    });

    test("should filter by format", async () => {
      const response = await fetch(
        `${API_URL}/media/search?format=jpeg`,
        {
          headers: {
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );

      const result = await response.json();
      expect(response.status).toBe(200);
      expect(Array.isArray(result)).toBe(true);
      result.forEach((media: any) => {
        if (media.format) {
          expect(media.format).toBe("jpeg");
        }
      });
    });
  });

  describe("Media Deletion", () => {
    test("should delete media file", async () => {
      // First upload a file to delete
      const formData = new FormData();
      const testFile = createTestFile(
        "to be deleted",
        "delete-me.txt",
        "text/plain"
      );
      formData.append("file", testFile);

      const uploadResponse = await fetch(`${API_URL}/media/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        body: formData,
      });

      const uploadResult = await uploadResponse.json();
      const mediaIdToDelete = uploadResult.media_id;

      // Now delete it
      const deleteResponse = await fetch(`${API_URL}/media/${mediaIdToDelete}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      const deleteResult = await deleteResponse.json();
      expect(deleteResponse.status).toBe(200);
      expect(deleteResult.message).toContain("deleted successfully");

      // Verify it's gone
      const getResponse = await fetch(`${API_URL}/media/${mediaIdToDelete}`, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });
      expect(getResponse.status).toBe(404);
    });
  });

  describe("Permission Checks", () => {
    let restrictedKey: string;

    beforeAll(async () => {
      // Create a read-only key
      const response = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Read-Only Media Key",
          permissions: [
            {
              resource: "media",
              actions: ["read"],
              constraints: null,
            },
          ],
        }),
      });
      const result = await response.json();
      restrictedKey = result.api_key;
    });

    test("should deny upload with read-only key", async () => {
      const formData = new FormData();
      const testFile = createTestFile("test", "test.txt", "text/plain");
      formData.append("file", testFile);

      const response = await fetch(`${API_URL}/media/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${restrictedKey}`,
        },
        body: formData,
      });

      expect(response.status).toBe(403);
      const result = await response.json();
      expect(result.detail).toContain("Insufficient permissions");
    });

    test("should allow read with read-only key", async () => {
      const response = await fetch(`${API_URL}/media/search`, {
        headers: {
          Authorization: `Bearer ${restrictedKey}`,
        },
      });

      expect(response.status).toBe(200);
    });
  });
});