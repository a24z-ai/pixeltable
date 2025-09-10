import { describe, test, expect } from "bun:test";
import PixeltableClient from "./index";

describe("PixeltableClient", () => {
  test("should create client with default config", () => {
    const client = new PixeltableClient();
    expect(client).toBeDefined();
  });

  test("should create client with custom baseUrl", () => {
    const client = new PixeltableClient({
      baseUrl: "http://example.com/api/v1"
    });
    expect(client).toBeDefined();
  });

  test("should create client with apiKey", () => {
    const client = new PixeltableClient({
      apiKey: "test-key"
    });
    expect(client).toBeDefined();
  });
});