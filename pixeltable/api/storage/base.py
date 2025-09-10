"""Base storage backend interface."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Any, List
from pathlib import Path
import hashlib
from uuid import UUID


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    async def store(self, file: BinaryIO, key: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a file and return its storage path."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> BinaryIO:
        """Retrieve a file by its key."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a file by its key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a file exists."""
        pass
    
    @abstractmethod
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing the file."""
        pass
    
    @abstractmethod
    async def get_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for a file."""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: Optional[str] = None, limit: int = 100) -> List[str]:
        """List files with optional prefix filter."""
        pass
    
    @abstractmethod
    async def get_size(self, key: str) -> int:
        """Get the size of a file in bytes."""
        pass
    
    def generate_key(self, media_id: UUID, filename: str, media_type: str) -> str:
        """Generate a storage key for a file."""
        # Extract extension from filename
        ext = Path(filename).suffix.lower()
        # Create a path structure: media_type/year/month/media_id.ext
        from datetime import datetime
        now = datetime.utcnow()
        return f"{media_type}/{now.year:04d}/{now.month:02d}/{media_id}{ext}"
    
    def calculate_hash(self, file: BinaryIO) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        file.seek(0)
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
        file.seek(0)
        return sha256_hash.hexdigest()


class StorageManager:
    """Manager for multiple storage backends."""
    
    def __init__(self):
        self.backends: Dict[str, StorageBackend] = {}
        self.default_backend: Optional[str] = None
    
    def register_backend(self, name: str, backend: StorageBackend, is_default: bool = False):
        """Register a storage backend."""
        self.backends[name] = backend
        if is_default or self.default_backend is None:
            self.default_backend = name
    
    def get_backend(self, name: Optional[str] = None) -> StorageBackend:
        """Get a storage backend by name or the default."""
        if name is None:
            name = self.default_backend
        if name not in self.backends:
            raise ValueError(f"Storage backend '{name}' not found")
        return self.backends[name]
    
    async def store(self, file: BinaryIO, key: str, backend: Optional[str] = None, 
                    metadata: Optional[Dict[str, Any]] = None) -> tuple[str, str]:
        """Store a file and return the backend name and storage path."""
        backend_obj = self.get_backend(backend)
        path = await backend_obj.store(file, key, metadata)
        return (backend or self.default_backend, path)
    
    async def retrieve(self, key: str, backend: Optional[str] = None) -> BinaryIO:
        """Retrieve a file."""
        backend_obj = self.get_backend(backend)
        return await backend_obj.retrieve(key)
    
    async def delete(self, key: str, backend: Optional[str] = None) -> bool:
        """Delete a file."""
        backend_obj = self.get_backend(backend)
        return await backend_obj.delete(key)
    
    async def get_url(self, key: str, backend: Optional[str] = None, 
                      expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file."""
        backend_obj = self.get_backend(backend)
        return await backend_obj.get_url(key, expires_in)