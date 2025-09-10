#!/usr/bin/env bun
/**
 * Generate TypeScript types from FastAPI OpenAPI schema
 */

import { $ } from "bun";

console.log("Fetching OpenAPI schema from FastAPI server...");
console.log("Make sure the API server is running: python -m pixeltable.api");

try {
  // Fetch the OpenAPI schema
  const response = await fetch("http://localhost:8000/openapi.json");
  if (!response.ok) {
    throw new Error(`Failed to fetch OpenAPI schema: ${response.statusText}`);
  }
  
  const schema = await response.json();
  
  // Save the schema temporarily
  await Bun.write("openapi.json", JSON.stringify(schema, null, 2));
  
  console.log("OpenAPI schema fetched successfully");
  console.log("Note: You can use tools like openapi-typescript to generate types from openapi.json");
  
  // For now, we'll generate basic types from the schema
  generateBasicTypes(schema);
  
} catch (error) {
  console.error("Error:", error);
  console.error("Make sure the FastAPI server is running: python -m pixeltable.api");
}

function generateBasicTypes(schema: any) {
  let types = `// Auto-generated types from OpenAPI schema\n\n`;
  
  // Extract schemas from components
  if (schema.components?.schemas) {
    for (const [name, def] of Object.entries(schema.components.schemas)) {
      types += generateInterface(name, def as any);
    }
  }
  
  // Write to file
  Bun.write("src/generated/api-types.ts", types);
  console.log("Basic types generated at src/generated/api-types.ts");
}

function generateInterface(name: string, schema: any): string {
  let result = `export interface ${name} {\n`;
  
  if (schema.properties) {
    for (const [prop, def] of Object.entries(schema.properties)) {
      const propDef = def as any;
      const required = schema.required?.includes(prop) ? "" : "?";
      const type = mapOpenAPIType(propDef);
      result += `  ${prop}${required}: ${type};\n`;
    }
  }
  
  result += `}\n\n`;
  return result;
}

function mapOpenAPIType(schema: any): string {
  if (schema.$ref) {
    // Extract type name from $ref
    return schema.$ref.split("/").pop();
  }
  
  switch (schema.type) {
    case "string":
      return "string";
    case "number":
    case "integer":
      return "number";
    case "boolean":
      return "boolean";
    case "array":
      return `Array<${mapOpenAPIType(schema.items)}>`;
    case "object":
      if (schema.additionalProperties) {
        return `Record<string, ${mapOpenAPIType(schema.additionalProperties)}>`;
      }
      return "any";
    default:
      return "any";
  }
}