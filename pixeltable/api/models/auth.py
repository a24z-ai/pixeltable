"""Authentication and authorization models for Pixeltable API."""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import secrets
import hashlib
from uuid import UUID, uuid4


class Permission(BaseModel):
    """Permission model for API access control."""
    resource: Literal['tables', 'data', 'media', 'admin'] = Field(..., description="Resource type")
    actions: List[Literal['read', 'write', 'delete', 'create']] = Field(..., description="Allowed actions")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Additional constraints (e.g., table names)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "resource": "tables",
                    "actions": ["read", "create"],
                    "constraints": {"table_names": ["users", "products"]}
                },
                {
                    "resource": "data",
                    "actions": ["read", "write"],
                    "constraints": None
                }
            ]
        }
    )


class CreateAPIKeyRequest(BaseModel):
    """Request to create a new API key."""
    name: str = Field(..., min_length=1, max_length=100, description="Descriptive name for the API key")
    permissions: List[Permission] = Field(..., description="Permissions granted to this API key")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Production Read-Only Key",
                    "permissions": [
                        {
                            "resource": "tables",
                            "actions": ["read"],
                            "constraints": None
                        },
                        {
                            "resource": "data",
                            "actions": ["read"],
                            "constraints": None
                        }
                    ],
                    "expires_at": "2025-12-31T23:59:59Z"
                }
            ]
        }
    )


class APIKeyInfo(BaseModel):
    """Information about an API key (without the actual key)."""
    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Descriptive name")
    key_prefix: str = Field(..., description="First 8 characters of the key for identification")
    permissions: List[Permission] = Field(..., description="Granted permissions")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    revoked: bool = Field(False, description="Whether the key has been revoked")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Production API Key",
                    "key_prefix": "pxt_live",
                    "permissions": [
                        {
                            "resource": "tables",
                            "actions": ["read", "write", "create", "delete"],
                            "constraints": None
                        }
                    ],
                    "created_at": "2025-01-10T12:00:00Z",
                    "last_used": "2025-01-10T14:30:00Z",
                    "expires_at": None,
                    "revoked": False
                }
            ]
        }
    )


class APIKeyResponse(BaseModel):
    """Response when creating a new API key."""
    api_key: str = Field(..., description="The actual API key (shown only once)")
    key_info: APIKeyInfo = Field(..., description="Information about the created key")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "api_key": "pxt_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                    "key_info": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Production API Key",
                        "key_prefix": "pxt_live",
                        "permissions": [],
                        "created_at": "2025-01-10T12:00:00Z",
                        "last_used": None,
                        "expires_at": None,
                        "revoked": False
                    }
                }
            ]
        }
    )


class RevokeAPIKeyRequest(BaseModel):
    """Request to revoke an API key."""
    key_id: Optional[UUID] = Field(None, description="Key ID to revoke")
    key_prefix: Optional[str] = Field(None, description="Key prefix to revoke")
    
    @field_validator('key_prefix')
    def validate_prefix_or_id(cls, v, values):
        if not v and not values.get('key_id'):
            raise ValueError("Either key_id or key_prefix must be provided")
        return v


class APIUsageStats(BaseModel):
    """API usage statistics for a key."""
    key_id: UUID = Field(..., description="API key identifier")
    endpoint_counts: Dict[str, int] = Field(..., description="Request counts by endpoint")
    status_code_counts: Dict[int, int] = Field(..., description="Request counts by status code")
    total_requests: int = Field(..., description="Total number of requests")
    avg_response_time_ms: float = Field(..., description="Average response time in milliseconds")
    period_start: datetime = Field(..., description="Start of statistics period")
    period_end: datetime = Field(..., description="End of statistics period")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    requests_per_minute: int = Field(60, ge=1, le=10000, description="Max requests per minute")
    requests_per_hour: int = Field(1000, ge=1, le=100000, description="Max requests per hour")
    burst_size: int = Field(10, ge=1, le=100, description="Max burst size")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "burst_size": 10
                }
            ]
        }
    )


class AuthContext(BaseModel):
    """Authentication context for a request."""
    api_key_id: UUID
    permissions: List[Permission]
    rate_limit: RateLimitConfig
    
    def has_permission(self, resource: str, action: str, table_name: Optional[str] = None) -> bool:
        """Check if the context has a specific permission."""
        for perm in self.permissions:
            if perm.resource != resource:
                continue
            if action not in perm.actions:
                continue
            if table_name and perm.constraints:
                allowed_tables = perm.constraints.get('table_names', [])
                if allowed_tables and table_name not in allowed_tables:
                    continue
            return True
        return False


def generate_api_key(prefix: str = "pxt") -> str:
    """Generate a secure API key."""
    # Generate 32 bytes of random data
    random_bytes = secrets.token_bytes(32)
    # Convert to hex string
    key_suffix = random_bytes.hex()[:32]
    # Add prefix for identification
    return f"{prefix}_{key_suffix}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, key_hash: str) -> bool:
    """Verify an API key against its hash."""
    return hash_api_key(api_key) == key_hash