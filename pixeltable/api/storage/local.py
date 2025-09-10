"""Local filesystem storage backend."""

import os
import shutil
import aiofiles
from pathlib import Path
from typing import BinaryIO, Optional, Dict, Any, List
from datetime import datetime
import json
import tempfile
import io

from .base import StorageBackend


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend implementation."""
    
    def __init__(self, base_path: str = "/tmp/pixeltable/media", 
                 public_base_url: str = "http://localhost:8000/media"):
        """Initialize local storage backend."""
        self.base_path = Path(base_path)
        self.public_base_url = public_base_url.rstrip('/')
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_suffix = ".meta.json"
    
    async def store(self, file: BinaryIO, key: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a file locally."""
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file.seek(0)
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := file.read(8192):
                await f.write(chunk)
        
        # Store metadata
        if metadata:
            meta_path = self.base_path / f"{key}{self.metadata_suffix}"
            async with aiofiles.open(meta_path, 'w') as f:
                await f.write(json.dumps(metadata, default=str))
        
        return str(file_path.relative_to(self.base_path))
    
    async def retrieve(self, key: str) -> BinaryIO:
        """Retrieve a file from local storage."""
        file_path = self.base_path / key
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        
        # Read file into memory
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        return io.BytesIO(content)
    
    async def delete(self, key: str) -> bool:
        """Delete a file from local storage."""
        file_path = self.base_path / key
        meta_path = self.base_path / f"{key}{self.metadata_suffix}"
        
        deleted = False
        if file_path.exists():
            file_path.unlink()
            deleted = True
        
        if meta_path.exists():
            meta_path.unlink()
        
        return deleted
    
    async def exists(self, key: str) -> bool:
        """Check if a file exists."""
        file_path = self.base_path / key
        return file_path.exists()
    
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a public URL for the file."""
        # For local storage, we return a simple URL
        # In production, this would be served by a web server like nginx
        return f"{self.public_base_url}/{key}"
    
    async def get_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for a file."""
        meta_path = self.base_path / f"{key}{self.metadata_suffix}"
        
        metadata = {}
        if meta_path.exists():
            async with aiofiles.open(meta_path, 'r') as f:
                content = await f.read()
                metadata = json.loads(content)
        
        # Add file system metadata
        file_path = self.base_path / key
        if file_path.exists():
            stat = file_path.stat()
            metadata.update({
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        
        return metadata
    
    async def list_files(self, prefix: Optional[str] = None, limit: int = 100) -> List[str]:
        """List files with optional prefix filter."""
        files = []
        search_path = self.base_path / prefix if prefix else self.base_path
        
        if search_path.exists():
            for file_path in search_path.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith(self.metadata_suffix):
                    relative_path = file_path.relative_to(self.base_path)
                    files.append(str(relative_path))
                    if len(files) >= limit:
                        break
        
        return files
    
    async def get_size(self, key: str) -> int:
        """Get the size of a file in bytes."""
        file_path = self.base_path / key
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return file_path.stat().st_size
    
    def cleanup_empty_dirs(self):
        """Clean up empty directories in the storage path."""
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                except OSError:
                    pass  # Directory not empty or other error