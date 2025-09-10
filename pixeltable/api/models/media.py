"""Media handling models for Pixeltable API."""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from uuid import UUID, uuid4
from enum import Enum


class MediaType(str, Enum):
    """Supported media types."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class MediaFormat(str, Enum):
    """Supported media formats."""
    # Images
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"
    
    # Videos
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    
    # Audio
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    M4A = "m4a"
    FLAC = "flac"
    
    # Documents
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    JSON = "json"
    
    UNKNOWN = "unknown"


class StorageBackend(str, Enum):
    """Storage backend types."""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"


class ProcessingOperation(str, Enum):
    """Media processing operations."""
    THUMBNAIL = "thumbnail"
    RESIZE = "resize"
    CROP = "crop"
    ROTATE = "rotate"
    CONVERT = "convert"
    EXTRACT_FRAMES = "extract_frames"
    EXTRACT_AUDIO = "extract_audio"
    EXTRACT_TEXT = "extract_text"
    EXTRACT_METADATA = "extract_metadata"


class MediaUploadRequest(BaseModel):
    """Request to upload media file."""
    table_name: Optional[str] = Field(None, description="Target table name")
    column_name: Optional[str] = Field(None, description="Target column name")
    row_id: Optional[str] = Field(None, description="Target row ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "table_name": "products",
                    "column_name": "image",
                    "row_id": "123",
                    "metadata": {"alt_text": "Product image"}
                }
            ]
        }
    )


class MediaURLIngestionRequest(BaseModel):
    """Request to ingest media from URL."""
    url: HttpUrl = Field(..., description="URL of the media file")
    table_name: Optional[str] = Field(None, description="Target table name")
    column_name: Optional[str] = Field(None, description="Target column name")
    row_id: Optional[str] = Field(None, description="Target row ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "url": "https://example.com/image.jpg",
                    "table_name": "products",
                    "column_name": "image",
                    "metadata": {"source": "external"}
                }
            ]
        }
    )


class MediaInfo(BaseModel):
    """Information about uploaded media."""
    media_id: UUID = Field(..., description="Unique media identifier")
    filename: str = Field(..., description="Original filename")
    media_type: MediaType = Field(..., description="Type of media")
    format: MediaFormat = Field(..., description="Media format")
    size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    storage_path: str = Field(..., description="Storage path or key")
    storage_backend: StorageBackend = Field(..., description="Storage backend used")
    url: Optional[str] = Field(None, description="Public URL if available")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL if available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "media_id": "550e8400-e29b-41d4-a716-446655440000",
                    "filename": "product.jpg",
                    "media_type": "image",
                    "format": "jpeg",
                    "size_bytes": 1024000,
                    "mime_type": "image/jpeg",
                    "storage_path": "media/images/550e8400-e29b-41d4-a716-446655440000.jpg",
                    "storage_backend": "local",
                    "url": "/api/v1/media/550e8400-e29b-41d4-a716-446655440000",
                    "thumbnail_url": "/api/v1/media/550e8400-e29b-41d4-a716-446655440000/thumbnail",
                    "metadata": {
                        "width": 1920,
                        "height": 1080,
                        "color_space": "RGB"
                    },
                    "created_at": "2025-01-10T12:00:00Z",
                    "updated_at": "2025-01-10T12:00:00Z"
                }
            ]
        }
    )


class MediaProcessingRequest(BaseModel):
    """Request to process media."""
    operation: ProcessingOperation = Field(..., description="Processing operation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    output_format: Optional[MediaFormat] = Field(None, description="Desired output format")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "operation": "thumbnail",
                    "parameters": {"width": 128, "height": 128}
                },
                {
                    "operation": "resize",
                    "parameters": {"width": 800, "height": 600, "maintain_aspect": True}
                },
                {
                    "operation": "convert",
                    "output_format": "webp"
                }
            ]
        }
    )


class ProcessingJob(BaseModel):
    """Media processing job status."""
    job_id: UUID = Field(..., description="Job identifier")
    media_id: UUID = Field(..., description="Source media ID")
    operation: ProcessingOperation = Field(..., description="Processing operation")
    parameters: Dict[str, Any] = Field(..., description="Operation parameters")
    status: Literal['pending', 'processing', 'completed', 'failed'] = Field(..., description="Job status")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    result_media_id: Optional[UUID] = Field(None, description="Result media ID if completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "job_id": "650e8400-e29b-41d4-a716-446655440000",
                    "media_id": "550e8400-e29b-41d4-a716-446655440000",
                    "operation": "thumbnail",
                    "parameters": {"width": 128, "height": 128},
                    "status": "completed",
                    "progress": 100.0,
                    "result_media_id": "750e8400-e29b-41d4-a716-446655440000",
                    "created_at": "2025-01-10T12:00:00Z",
                    "completed_at": "2025-01-10T12:00:05Z"
                }
            ]
        }
    )


class MediaMetadata(BaseModel):
    """Extracted media metadata."""
    width: Optional[int] = Field(None, description="Width in pixels (images/video)")
    height: Optional[int] = Field(None, description="Height in pixels (images/video)")
    duration_seconds: Optional[float] = Field(None, description="Duration (video/audio)")
    frame_rate: Optional[float] = Field(None, description="Frame rate (video)")
    bit_rate: Optional[int] = Field(None, description="Bit rate (video/audio)")
    codec: Optional[str] = Field(None, description="Codec information")
    color_space: Optional[str] = Field(None, description="Color space (images)")
    channels: Optional[int] = Field(None, description="Audio channels")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate")
    page_count: Optional[int] = Field(None, description="Page count (documents)")
    word_count: Optional[int] = Field(None, description="Word count (documents)")
    author: Optional[str] = Field(None, description="Author (documents)")
    title: Optional[str] = Field(None, description="Title metadata")
    tags: Optional[List[str]] = Field(None, description="Tags or keywords")
    location: Optional[Dict[str, float]] = Field(None, description="GPS location if available")
    camera_info: Optional[Dict[str, str]] = Field(None, description="Camera/device information")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "width": 1920,
                    "height": 1080,
                    "color_space": "sRGB",
                    "camera_info": {
                        "make": "Canon",
                        "model": "EOS R5",
                        "lens": "24-70mm"
                    },
                    "location": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    }
                }
            ]
        }
    )


class StorageConfig(BaseModel):
    """Storage backend configuration."""
    backend: StorageBackend = Field(..., description="Storage backend type")
    config: Dict[str, Any] = Field(..., description="Backend-specific configuration")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "backend": "local",
                    "config": {
                        "base_path": "/var/pixeltable/media",
                        "public_base_url": "http://localhost:8000/media"
                    }
                },
                {
                    "backend": "s3",
                    "config": {
                        "bucket": "pixeltable-media",
                        "region": "us-west-2",
                        "access_key": "***",
                        "secret_key": "***",
                        "public_base_url": "https://cdn.example.com"
                    }
                }
            ]
        }
    )


class BulkMediaUploadRequest(BaseModel):
    """Request for bulk media upload."""
    table_name: str = Field(..., description="Target table name")
    column_name: str = Field(..., description="Target column name")
    files_metadata: List[Dict[str, Any]] = Field(..., description="Metadata for each file to be uploaded")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "table_name": "products",
                    "column_name": "images",
                    "files_metadata": [
                        {"filename": "product1.jpg", "row_id": "1"},
                        {"filename": "product2.jpg", "row_id": "2"}
                    ]
                }
            ]
        }
    )


class MediaSearchRequest(BaseModel):
    """Request to search media."""
    query: Optional[str] = Field(None, description="Text query for similarity search")
    media_type: Optional[MediaType] = Field(None, description="Filter by media type")
    format: Optional[MediaFormat] = Field(None, description="Filter by format")
    min_size_bytes: Optional[int] = Field(None, description="Minimum file size")
    max_size_bytes: Optional[int] = Field(None, description="Maximum file size")
    created_after: Optional[datetime] = Field(None, description="Created after this date")
    created_before: Optional[datetime] = Field(None, description="Created before this date")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Filter by metadata")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")
    offset: int = Field(0, ge=0, description="Results offset")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "query": "sunset beach",
                    "media_type": "image",
                    "limit": 10,
                    "metadata_filters": {"tags": ["nature", "landscape"]}
                }
            ]
        }
    )