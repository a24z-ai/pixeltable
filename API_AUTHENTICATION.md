# Pixeltable API Authentication & Security Documentation

## Overview
This document describes the authentication and security features implemented in Milestone 2 Phase 2 of the Pixeltable API development.

## Authentication Methods

### API Key Authentication

The Pixeltable API supports two methods of providing API keys:

#### 1. Bearer Token (Recommended)
```http
Authorization: Bearer pxt_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

#### 2. X-API-Key Header
```http
X-API-Key: pxt_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

## API Key Management Endpoints

### Create API Key
```http
POST /api/v1/auth/api-keys
Content-Type: application/json

{
  "name": "Production API Key",
  "permissions": [
    {
      "resource": "tables",
      "actions": ["read", "write", "create", "delete"],
      "constraints": null
    },
    {
      "resource": "data",
      "actions": ["read", "write"],
      "constraints": {
        "table_names": ["users", "products"]
      }
    }
  ],
  "expires_at": "2025-12-31T23:59:59Z"  // Optional
}
```

**Response:**
```json
{
  "api_key": "pxt_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "key_info": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Production API Key",
    "key_prefix": "pxt_live",
    "permissions": [...],
    "created_at": "2025-01-10T12:00:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "revoked": false
  }
}
```

**Important:** The `api_key` value is only shown once. Store it securely.

### List API Keys
```http
GET /api/v1/auth/api-keys
Authorization: Bearer {your-api-key}
```

Returns a list of all API keys (without the actual key values).

### Get API Key Info
```http
GET /api/v1/auth/api-keys/{key_id}
Authorization: Bearer {your-api-key}
```

### Revoke API Key
```http
POST /api/v1/auth/api-keys/revoke
Authorization: Bearer {your-api-key}
Content-Type: application/json

{
  "key_id": "550e8400-e29b-41d4-a716-446655440000"
  // OR
  "key_prefix": "pxt_live"
}
```

### Rotate API Key
```http
POST /api/v1/auth/api-keys/{key_id}/rotate
Authorization: Bearer {your-api-key}
```

Creates a new key with the same permissions and revokes the old one.

### Get API Key Usage Statistics
```http
GET /api/v1/auth/api-keys/{key_id}/usage?hours=24
Authorization: Bearer {your-api-key}
```

**Response:**
```json
{
  "key_id": "550e8400-e29b-41d4-a716-446655440000",
  "endpoint_counts": {
    "/api/v1/tables": 150,
    "/api/v1/tables/users/rows": 300
  },
  "status_code_counts": {
    "200": 400,
    "400": 45,
    "429": 5
  },
  "total_requests": 450,
  "avg_response_time_ms": 125.5,
  "period_start": "2025-01-09T12:00:00Z",
  "period_end": "2025-01-10T12:00:00Z"
}
```

### Verify Current Authentication
```http
GET /api/v1/auth/verify
Authorization: Bearer {your-api-key}
```

## Permission System

### Resources and Actions

Permissions are defined by resource type and allowed actions:

| Resource | Available Actions | Description |
|----------|------------------|-------------|
| `tables` | `read`, `write`, `create`, `delete` | Table management operations |
| `data` | `read`, `write`, `create`, `delete` | Data operations within tables |
| `media` | `read`, `write`, `create`, `delete` | Media file operations |
| `admin` | `create`, `read`, `write`, `delete` | Administrative operations |

### Permission Constraints

Permissions can include constraints to limit access:

```json
{
  "resource": "data",
  "actions": ["read", "write"],
  "constraints": {
    "table_names": ["users", "products"]  // Only access these tables
  }
}
```

### Example Permission Sets

#### Read-Only Access
```json
{
  "permissions": [
    {
      "resource": "tables",
      "actions": ["read"],
      "constraints": null
    },
    {
      "resource": "data",
      "actions": ["read"],
      "constraints": null
    }
  ]
}
```

#### Table-Specific Write Access
```json
{
  "permissions": [
    {
      "resource": "data",
      "actions": ["read", "write"],
      "constraints": {
        "table_names": ["analytics_events"]
      }
    }
  ]
}
```

#### Full Admin Access
```json
{
  "permissions": [
    {
      "resource": "tables",
      "actions": ["read", "write", "create", "delete"],
      "constraints": null
    },
    {
      "resource": "data",
      "actions": ["read", "write", "create", "delete"],
      "constraints": null
    },
    {
      "resource": "admin",
      "actions": ["read", "write", "create", "delete"],
      "constraints": null
    }
  ]
}
```

## Rate Limiting

### Default Limits

- **Requests per minute**: 60
- **Requests per hour**: 1000
- **Burst size**: 10

### Rate Limit Headers

All API responses include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704902400
```

When rate limited (429 response):
```http
Retry-After: 30
```

### Custom Rate Limits

Different API keys can have different rate limits based on their tier or usage requirements.

## JavaScript/TypeScript SDK Usage

### Authentication Setup

```typescript
import PixeltableClient from '@pixeltable/sdk';

const client = new PixeltableClient({
  baseUrl: 'http://localhost:8000/api/v1',
  apiKey: 'pxt_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
});
```

### API Key Management

```typescript
// Create an API key
const { api_key, key_info } = await client.createAPIKey({
  name: 'Production Key',
  permissions: [
    {
      resource: 'tables',
      actions: ['read', 'write', 'create', 'delete'],
      constraints: null
    }
  ],
  expires_at: '2025-12-31T23:59:59Z'
});

// Store the api_key securely - it won't be shown again!
console.log('New API Key:', api_key);

// List all API keys
const keys = await client.listAPIKeys();

// Get specific key info
const keyInfo = await client.getAPIKey(key_info.id);

// Rotate a key
const { api_key: newKey } = await client.rotateAPIKey(key_info.id);

// Revoke a key
await client.revokeAPIKey(key_info.id);

// Get usage statistics
const stats = await client.getAPIKeyUsage(key_info.id, 24); // Last 24 hours

// Verify current authentication
const auth = await client.verifyAuth();
console.log('Permissions:', auth.permissions);
```

## Security Best Practices

### API Key Storage

1. **Never commit API keys** to version control
2. **Use environment variables** for production keys
3. **Rotate keys regularly** using the rotation endpoint
4. **Set expiration dates** for temporary keys

### Environment Variables

```bash
# .env file (add to .gitignore!)
PIXELTABLE_API_KEY=pxt_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

```typescript
// Use in code
const client = new PixeltableClient({
  apiKey: process.env.PIXELTABLE_API_KEY
});
```

### Least Privilege Principle

Always create API keys with the minimum permissions required:

```typescript
// Bad: Full access for a read-only dashboard
const key = await client.createAPIKey({
  name: 'Dashboard',
  permissions: [
    { resource: 'tables', actions: ['read', 'write', 'create', 'delete'] }
  ]
});

// Good: Read-only access for dashboard
const key = await client.createAPIKey({
  name: 'Dashboard Read-Only',
  permissions: [
    { resource: 'tables', actions: ['read'] },
    { resource: 'data', actions: ['read'] }
  ]
});
```

## Error Handling

### Authentication Errors

| Status Code | Description | Action |
|------------|-------------|--------|
| 401 | Invalid or expired API key | Check key validity, rotate if needed |
| 403 | Insufficient permissions | Request additional permissions |
| 429 | Rate limit exceeded | Wait and retry with exponential backoff |

### Example Error Handling

```typescript
try {
  const tables = await client.listTables();
} catch (error) {
  if (error.message.includes('401')) {
    console.error('Invalid API key - please check your credentials');
  } else if (error.message.includes('429')) {
    console.error('Rate limited - waiting before retry...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    // Retry operation
  } else {
    console.error('API error:', error.message);
  }
}
```

## Migration Guide

### From Unauthenticated to Authenticated API

1. **Create an API key** with appropriate permissions
2. **Update client initialization** to include the API key
3. **Test with limited permissions** before granting full access
4. **Monitor usage** through the statistics endpoint
5. **Set up key rotation** schedule for production

### Gradual Rollout

The API currently supports optional authentication (`require_auth=False`). To migrate:

1. Start by creating and testing API keys
2. Update clients to use authentication
3. Monitor unauthenticated requests
4. Enable required authentication when ready

## Troubleshooting

### Common Issues

#### "Invalid API key" Error
- Verify the key hasn't been revoked
- Check expiration date
- Ensure correct header format (Bearer prefix)

#### Rate Limiting Issues
- Check current usage with statistics endpoint
- Consider requesting higher limits
- Implement exponential backoff

#### Permission Denied
- Verify key permissions with `/auth/verify`
- Check resource and action requirements
- Review constraint limitations

## Future Enhancements

- OAuth 2.0 support
- JWT token authentication
- Role-based access control (RBAC)
- IP allowlisting
- Webhook authentication
- Multi-factor authentication (MFA)

## Support

For authentication issues or security questions, please refer to:
- [API Documentation](https://github.com/a24z-ai/pixeltable)
- [Security Best Practices](https://github.com/a24z-ai/pixeltable/security)
- [Issue Tracker](https://github.com/a24z-ai/pixeltable/issues)