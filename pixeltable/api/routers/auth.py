"""Authentication and API key management endpoints."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import pixeltable as pxt
from pixeltable.api.models.auth import (
    CreateAPIKeyRequest,
    APIKeyInfo,
    APIKeyResponse,
    RevokeAPIKeyRequest,
    APIUsageStats,
    Permission,
    RateLimitConfig,
    AuthContext,
    generate_api_key,
    hash_api_key,
    verify_api_key,
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory storage for API keys (should be replaced with database in production)
# This is a temporary implementation for demonstration
api_keys_store: Dict[UUID, Dict[str, Any]] = {}
api_keys_by_hash: Dict[str, UUID] = {}
api_usage_store: Dict[UUID, List[Dict[str, Any]]] = {}

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract API key from request headers."""
    # Check Bearer token first
    if credentials and credentials.credentials:
        return credentials.credentials
    # Check X-API-Key header
    if x_api_key:
        return x_api_key
    return None


async def verify_api_key_auth(api_key: Optional[str] = Depends(get_current_api_key)) -> AuthContext:
    """Verify API key and return auth context."""
    if not api_key:
        # For now, allow unauthenticated access with full permissions
        # In production, this should raise an exception
        return AuthContext(
            api_key_id=uuid4(),
            permissions=[
                Permission(resource="tables", actions=["read", "write", "create", "delete"]),
                Permission(resource="data", actions=["read", "write", "create", "delete"]),
                Permission(resource="media", actions=["read", "write", "create", "delete"]),
            ],
            rate_limit=RateLimitConfig()
        )
    
    # Hash the provided key and look it up
    key_hash = hash_api_key(api_key)
    if key_hash not in api_keys_by_hash:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_id = api_keys_by_hash[key_hash]
    key_data = api_keys_store.get(key_id)
    
    if not key_data:
        raise HTTPException(status_code=401, detail="API key not found")
    
    # Check if key is revoked
    if key_data.get('revoked', False):
        raise HTTPException(status_code=401, detail="API key has been revoked")
    
    # Check expiration
    expires_at = key_data.get('expires_at')
    if expires_at and datetime.fromisoformat(expires_at) < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key has expired")
    
    # Update last used timestamp
    key_data['last_used'] = datetime.utcnow().isoformat()
    
    # Record usage
    if key_id not in api_usage_store:
        api_usage_store[key_id] = []
    
    return AuthContext(
        api_key_id=key_id,
        permissions=key_data['permissions'],
        rate_limit=key_data.get('rate_limit', RateLimitConfig())
    )


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> APIKeyResponse:
    """Create a new API key."""
    # Check if user has permission to create API keys
    if not auth.has_permission("admin", "create"):
        # For demo purposes, allow anyone to create keys
        # In production, this should be restricted
        pass
    
    # Generate new API key
    key_prefix = "pxt_live" if "write" in [a for p in request.permissions for a in p.actions] else "pxt_read"
    api_key = generate_api_key(key_prefix)
    key_hash = hash_api_key(api_key)
    key_id = uuid4()
    
    # Store key information
    key_info = {
        'id': key_id,
        'name': request.name,
        'key_prefix': api_key[:8],
        'key_hash': key_hash,
        'permissions': [p.model_dump() for p in request.permissions],
        'created_at': datetime.utcnow().isoformat(),
        'last_used': None,
        'expires_at': request.expires_at.isoformat() if request.expires_at else None,
        'revoked': False,
        'rate_limit': RateLimitConfig().model_dump()
    }
    
    api_keys_store[key_id] = key_info
    api_keys_by_hash[key_hash] = key_id
    
    # Return response with the actual key (shown only once)
    return APIKeyResponse(
        api_key=api_key,
        key_info=APIKeyInfo(
            id=key_id,
            name=request.name,
            key_prefix=api_key[:8],
            permissions=request.permissions,
            created_at=datetime.fromisoformat(key_info['created_at']),
            last_used=None,
            expires_at=request.expires_at,
            revoked=False
        )
    )


@router.get("/api-keys", response_model=List[APIKeyInfo])
async def list_api_keys(
    auth: AuthContext = Depends(verify_api_key_auth)
) -> List[APIKeyInfo]:
    """List all API keys (without the actual keys)."""
    keys = []
    for key_id, key_data in api_keys_store.items():
        keys.append(APIKeyInfo(
            id=key_id,
            name=key_data['name'],
            key_prefix=key_data['key_prefix'],
            permissions=[Permission(**p) for p in key_data['permissions']],
            created_at=datetime.fromisoformat(key_data['created_at']),
            last_used=datetime.fromisoformat(key_data['last_used']) if key_data['last_used'] else None,
            expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data['expires_at'] else None,
            revoked=key_data['revoked']
        ))
    return keys


@router.get("/api-keys/{key_id}", response_model=APIKeyInfo)
async def get_api_key(
    key_id: UUID,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> APIKeyInfo:
    """Get information about a specific API key."""
    if key_id not in api_keys_store:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key_data = api_keys_store[key_id]
    return APIKeyInfo(
        id=key_id,
        name=key_data['name'],
        key_prefix=key_data['key_prefix'],
        permissions=[Permission(**p) for p in key_data['permissions']],
        created_at=datetime.fromisoformat(key_data['created_at']),
        last_used=datetime.fromisoformat(key_data['last_used']) if key_data['last_used'] else None,
        expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data['expires_at'] else None,
        revoked=key_data['revoked']
    )


@router.post("/api-keys/revoke")
async def revoke_api_key(
    request: RevokeAPIKeyRequest,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> Dict[str, str]:
    """Revoke an API key."""
    key_id = None
    
    if request.key_id:
        key_id = request.key_id
    elif request.key_prefix:
        # Find key by prefix
        for kid, key_data in api_keys_store.items():
            if key_data['key_prefix'] == request.key_prefix:
                key_id = kid
                break
    
    if not key_id or key_id not in api_keys_store:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Revoke the key
    api_keys_store[key_id]['revoked'] = True
    
    # Remove from hash lookup
    key_hash = api_keys_store[key_id]['key_hash']
    if key_hash in api_keys_by_hash:
        del api_keys_by_hash[key_hash]
    
    return {"message": f"API key {api_keys_store[key_id]['key_prefix']}... has been revoked"}


@router.post("/api-keys/{key_id}/rotate", response_model=APIKeyResponse)
async def rotate_api_key(
    key_id: UUID,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> APIKeyResponse:
    """Rotate an API key (revoke old, create new with same permissions)."""
    if key_id not in api_keys_store:
        raise HTTPException(status_code=404, detail="API key not found")
    
    old_key_data = api_keys_store[key_id]
    
    # Revoke old key
    old_key_data['revoked'] = True
    old_key_hash = old_key_data['key_hash']
    if old_key_hash in api_keys_by_hash:
        del api_keys_by_hash[old_key_hash]
    
    # Create new key with same permissions
    key_prefix = old_key_data['key_prefix'][:8]
    new_api_key = generate_api_key(key_prefix)
    new_key_hash = hash_api_key(new_api_key)
    new_key_id = uuid4()
    
    # Store new key
    new_key_info = {
        'id': new_key_id,
        'name': old_key_data['name'] + " (rotated)",
        'key_prefix': new_api_key[:8],
        'key_hash': new_key_hash,
        'permissions': old_key_data['permissions'],
        'created_at': datetime.utcnow().isoformat(),
        'last_used': None,
        'expires_at': old_key_data['expires_at'],
        'revoked': False,
        'rate_limit': old_key_data.get('rate_limit', RateLimitConfig().model_dump())
    }
    
    api_keys_store[new_key_id] = new_key_info
    api_keys_by_hash[new_key_hash] = new_key_id
    
    return APIKeyResponse(
        api_key=new_api_key,
        key_info=APIKeyInfo(
            id=new_key_id,
            name=new_key_info['name'],
            key_prefix=new_api_key[:8],
            permissions=[Permission(**p) for p in new_key_info['permissions']],
            created_at=datetime.fromisoformat(new_key_info['created_at']),
            last_used=None,
            expires_at=datetime.fromisoformat(new_key_info['expires_at']) if new_key_info['expires_at'] else None,
            revoked=False
        )
    )


@router.get("/api-keys/{key_id}/usage", response_model=APIUsageStats)
async def get_api_key_usage(
    key_id: UUID,
    hours: int = 24,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> APIUsageStats:
    """Get usage statistics for an API key."""
    if key_id not in api_keys_store:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Calculate time range
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(hours=hours)
    
    # Get usage data (mock data for now)
    usage_data = api_usage_store.get(key_id, [])
    
    # Calculate statistics
    endpoint_counts = {}
    status_code_counts = {}
    total_time = 0
    total_requests = 0
    
    for usage in usage_data:
        # Filter by time range
        if 'timestamp' in usage:
            usage_time = datetime.fromisoformat(usage['timestamp'])
            if usage_time < period_start or usage_time > period_end:
                continue
        
        # Count endpoints
        endpoint = usage.get('endpoint', 'unknown')
        endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        
        # Count status codes
        status_code = usage.get('status_code', 200)
        status_code_counts[status_code] = status_code_counts.get(status_code, 0) + 1
        
        # Sum response times
        total_time += usage.get('response_time_ms', 0)
        total_requests += 1
    
    avg_response_time = total_time / total_requests if total_requests > 0 else 0
    
    return APIUsageStats(
        key_id=key_id,
        endpoint_counts=endpoint_counts,
        status_code_counts=status_code_counts,
        total_requests=total_requests,
        avg_response_time_ms=avg_response_time,
        period_start=period_start,
        period_end=period_end
    )


@router.get("/verify")
async def verify_current_key(auth: AuthContext = Depends(verify_api_key_auth)) -> Dict[str, Any]:
    """Verify the current API key and return its permissions."""
    return {
        "valid": True,
        "api_key_id": str(auth.api_key_id),
        "permissions": [p.model_dump() for p in auth.permissions],
        "rate_limit": auth.rate_limit.model_dump()
    }