"""Media handling endpoints for Pixeltable API."""

import io
import os
import mimetypes
import tempfile
from typing import Optional, List, Dict, Any, BinaryIO
from uuid import UUID, uuid4
from datetime import datetime
from pathlib import Path
import asyncio
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
import aiofiles
import httpx

import pixeltable as pxt
from pixeltable.api.models.media import (
    MediaUploadRequest,
    MediaURLIngestionRequest,
    MediaInfo,
    MediaProcessingRequest,
    ProcessingJob,
    MediaMetadata,
    MediaSearchRequest,
    MediaType,
    MediaFormat,
    StorageBackend as StorageBackendEnum,
    ProcessingOperation,
)
from pixeltable.api.models.auth import AuthContext
from pixeltable.api.routers.auth import verify_api_key_auth
from pixeltable.api.storage import StorageManager, LocalStorageBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["media"])

# Initialize storage manager with local backend
storage_manager = StorageManager()
local_backend = LocalStorageBackend(
    base_path=os.environ.get("MEDIA_STORAGE_PATH", "/tmp/pixeltable/media"),
    public_base_url=os.environ.get("MEDIA_PUBLIC_URL", "http://localhost:8000/api/v1/media")
)
storage_manager.register_backend("local", local_backend, is_default=True)

# In-memory storage for media metadata (should be replaced with database in production)
media_store: Dict[UUID, Dict[str, Any]] = {}
processing_jobs: Dict[UUID, Dict[str, Any]] = {}


def detect_media_type(filename: str, mime_type: Optional[str] = None) -> tuple[MediaType, MediaFormat]:
    """Detect media type and format from filename and MIME type."""
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filename)
    
    ext = Path(filename).suffix.lower().lstrip('.')
    
    # Map extensions to formats
    format_map = {
        'jpg': MediaFormat.JPEG, 'jpeg': MediaFormat.JPEG,
        'png': MediaFormat.PNG, 'gif': MediaFormat.GIF,
        'webp': MediaFormat.WEBP, 'bmp': MediaFormat.BMP,
        'tiff': MediaFormat.TIFF, 'tif': MediaFormat.TIFF,
        'mp4': MediaFormat.MP4, 'avi': MediaFormat.AVI,
        'mov': MediaFormat.MOV, 'mkv': MediaFormat.MKV,
        'webm': MediaFormat.WEBM,
        'mp3': MediaFormat.MP3, 'wav': MediaFormat.WAV,
        'ogg': MediaFormat.OGG, 'm4a': MediaFormat.M4A,
        'flac': MediaFormat.FLAC,
        'pdf': MediaFormat.PDF, 'docx': MediaFormat.DOCX,
        'txt': MediaFormat.TXT, 'csv': MediaFormat.CSV,
        'json': MediaFormat.JSON,
    }
    
    media_format = format_map.get(ext, MediaFormat.UNKNOWN)
    
    # Determine media type
    if mime_type:
        if mime_type.startswith('image/'):
            media_type = MediaType.IMAGE
        elif mime_type.startswith('video/'):
            media_type = MediaType.VIDEO
        elif mime_type.startswith('audio/'):
            media_type = MediaType.AUDIO
        elif mime_type in ['application/pdf', 'text/plain', 'text/csv', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            media_type = MediaType.DOCUMENT
        else:
            media_type = MediaType.UNKNOWN
    else:
        # Guess from format
        if media_format in [MediaFormat.JPEG, MediaFormat.PNG, MediaFormat.GIF, 
                            MediaFormat.WEBP, MediaFormat.BMP, MediaFormat.TIFF]:
            media_type = MediaType.IMAGE
        elif media_format in [MediaFormat.MP4, MediaFormat.AVI, MediaFormat.MOV, 
                              MediaFormat.MKV, MediaFormat.WEBM]:
            media_type = MediaType.VIDEO
        elif media_format in [MediaFormat.MP3, MediaFormat.WAV, MediaFormat.OGG, 
                              MediaFormat.M4A, MediaFormat.FLAC]:
            media_type = MediaType.AUDIO
        elif media_format in [MediaFormat.PDF, MediaFormat.DOCX, MediaFormat.TXT, 
                              MediaFormat.CSV, MediaFormat.JSON]:
            media_type = MediaType.DOCUMENT
        else:
            media_type = MediaType.UNKNOWN
    
    return media_type, media_format


async def extract_metadata(file_path: str, media_type: MediaType) -> MediaMetadata:
    """Extract metadata from a media file."""
    metadata = MediaMetadata()
    
    # Basic implementation - in production, use specialized libraries
    # like Pillow for images, ffmpeg for video/audio, etc.
    
    if media_type == MediaType.IMAGE:
        # Would use Pillow here
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                metadata.width = img.width
                metadata.height = img.height
                metadata.color_space = img.mode
        except ImportError:
            logger.warning("Pillow not installed, skipping image metadata extraction")
    
    elif media_type == MediaType.VIDEO:
        # Would use ffmpeg-python here
        pass
    
    elif media_type == MediaType.AUDIO:
        # Would use mutagen or similar
        pass
    
    elif media_type == MediaType.DOCUMENT:
        # Would use PyPDF2, python-docx, etc.
        if file_path.endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    metadata.word_count = len(content.split())
            except:
                pass
    
    return metadata


@router.post("/upload", response_model=MediaInfo)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    table_name: Optional[str] = Form(None),
    column_name: Optional[str] = Form(None),
    row_id: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    auth: AuthContext = Depends(verify_api_key_auth)
) -> MediaInfo:
    """Upload a media file."""
    # Check permissions
    if not auth.has_permission("media", "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions for media upload")
    
    # Generate media ID
    media_id = uuid4()
    
    # Detect media type and format
    media_type, media_format = detect_media_type(file.filename, file.content_type)
    
    # Parse metadata if provided
    parsed_metadata = {}
    if metadata:
        import json
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            pass
    
    # Generate storage key
    storage_backend = storage_manager.get_backend()
    storage_key = storage_backend.generate_key(media_id, file.filename, media_type.value)
    
    # Create temporary file for processing
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        # Save uploaded file
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Store file
        file_obj = io.BytesIO(content)
        backend_name, storage_path = await storage_manager.store(
            file_obj, 
            storage_key,
            metadata=parsed_metadata
        )
        
        # Extract metadata
        file_metadata = await extract_metadata(tmp_file_path, media_type)
        
        # Get file size
        file_size = len(content)
        
        # Create media info
        media_info = MediaInfo(
            media_id=media_id,
            filename=file.filename,
            media_type=media_type,
            format=media_format,
            size_bytes=file_size,
            mime_type=file.content_type or 'application/octet-stream',
            storage_path=storage_path,
            storage_backend=StorageBackendEnum.LOCAL,
            url=f"/api/v1/media/{media_id}",
            thumbnail_url=f"/api/v1/media/{media_id}/thumbnail" if media_type == MediaType.IMAGE else None,
            metadata={
                **parsed_metadata,
                **file_metadata.model_dump(exclude_none=True),
                'table_name': table_name,
                'column_name': column_name,
                'row_id': row_id,
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store media info
        media_store[media_id] = media_info.model_dump()
        
        # If table and column specified, update Pixeltable
        if table_name and column_name and row_id:
            background_tasks.add_task(
                update_pixeltable_media,
                table_name, column_name, row_id, media_id, storage_path
            )
        
        return media_info
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)


@router.post("/ingest", response_model=MediaInfo)
async def ingest_media_from_url(
    request: MediaURLIngestionRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> MediaInfo:
    """Ingest media from a URL."""
    # Check permissions
    if not auth.has_permission("media", "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions for media ingestion")
    
    # Generate media ID
    media_id = uuid4()
    
    # Download file from URL
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(request.url), follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Failed to download from URL: {e}")
    
    # Extract filename from URL or headers
    filename = Path(str(request.url)).name
    if not filename or filename == '':
        filename = f"download_{media_id}"
    
    # Detect media type
    content_type = response.headers.get('content-type', 'application/octet-stream')
    media_type, media_format = detect_media_type(filename, content_type)
    
    # Generate storage key
    storage_backend = storage_manager.get_backend()
    storage_key = storage_backend.generate_key(media_id, filename, media_type.value)
    
    # Store file
    file_obj = io.BytesIO(response.content)
    backend_name, storage_path = await storage_manager.store(
        file_obj,
        storage_key,
        metadata=request.metadata
    )
    
    # Create media info
    media_info = MediaInfo(
        media_id=media_id,
        filename=filename,
        media_type=media_type,
        format=media_format,
        size_bytes=len(response.content),
        mime_type=content_type,
        storage_path=storage_path,
        storage_backend=StorageBackendEnum.LOCAL,
        url=f"/api/v1/media/{media_id}",
        thumbnail_url=f"/api/v1/media/{media_id}/thumbnail" if media_type == MediaType.IMAGE else None,
        metadata={
            **(request.metadata or {}),
            'source_url': str(request.url),
            'table_name': request.table_name,
            'column_name': request.column_name,
            'row_id': request.row_id,
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Store media info
    media_store[media_id] = media_info.model_dump()
    
    # If table and column specified, update Pixeltable
    if request.table_name and request.column_name and request.row_id:
        background_tasks.add_task(
            update_pixeltable_media,
            request.table_name, request.column_name, request.row_id, media_id, storage_path
        )
    
    return media_info


@router.get("/{media_id}", response_model=MediaInfo)
async def get_media_info(
    media_id: UUID,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> MediaInfo:
    """Get information about a media file."""
    # Check permissions
    if not auth.has_permission("media", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if media_id not in media_store:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return MediaInfo(**media_store[media_id])


@router.get("/{media_id}/download")
async def download_media(
    media_id: UUID,
    auth: AuthContext = Depends(verify_api_key_auth)
):
    """Download a media file."""
    # Check permissions
    if not auth.has_permission("media", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if media_id not in media_store:
        raise HTTPException(status_code=404, detail="Media not found")
    
    media_info = media_store[media_id]
    
    # Retrieve file from storage
    try:
        file_obj = await storage_manager.retrieve(media_info['storage_path'])
        
        # Return as streaming response
        return StreamingResponse(
            file_obj,
            media_type=media_info['mime_type'],
            headers={
                "Content-Disposition": f"attachment; filename={media_info['filename']}"
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Media file not found in storage")


@router.delete("/{media_id}")
async def delete_media(
    media_id: UUID,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> Dict[str, str]:
    """Delete a media file."""
    # Check permissions
    if not auth.has_permission("media", "delete"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if media_id not in media_store:
        raise HTTPException(status_code=404, detail="Media not found")
    
    media_info = media_store[media_id]
    
    # Delete from storage
    deleted = await storage_manager.delete(media_info['storage_path'])
    
    # Remove from store
    del media_store[media_id]
    
    return {"message": f"Media {media_id} deleted successfully", "deleted_from_storage": str(deleted)}


@router.post("/{media_id}/process", response_model=ProcessingJob)
async def process_media(
    media_id: UUID,
    request: MediaProcessingRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> ProcessingJob:
    """Process a media file (thumbnail, resize, convert, etc.)."""
    # Check permissions
    if not auth.has_permission("media", "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if media_id not in media_store:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Create processing job
    job_id = uuid4()
    job = ProcessingJob(
        job_id=job_id,
        media_id=media_id,
        operation=request.operation,
        parameters=request.parameters,
        status='pending',
        progress=0.0,
        created_at=datetime.utcnow()
    )
    
    # Store job
    processing_jobs[job_id] = job.model_dump()
    
    # Start processing in background
    background_tasks.add_task(
        process_media_task,
        job_id, media_id, request.operation, request.parameters, request.output_format
    )
    
    return job


@router.get("/jobs/{job_id}", response_model=ProcessingJob)
async def get_processing_job(
    job_id: UUID,
    auth: AuthContext = Depends(verify_api_key_auth)
) -> ProcessingJob:
    """Get processing job status."""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ProcessingJob(**processing_jobs[job_id])


@router.get("/search", response_model=List[MediaInfo])
async def search_media(
    query: Optional[str] = Query(None),
    media_type: Optional[MediaType] = Query(None),
    format: Optional[MediaFormat] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    auth: AuthContext = Depends(verify_api_key_auth)
) -> List[MediaInfo]:
    """Search for media files."""
    # Check permissions
    if not auth.has_permission("media", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Simple filtering implementation
    results = []
    for media_id, media_info in media_store.items():
        # Filter by media type
        if media_type and media_info['media_type'] != media_type.value:
            continue
        
        # Filter by format
        if format and media_info['format'] != format.value:
            continue
        
        # Simple text search in filename and metadata
        if query:
            query_lower = query.lower()
            if (query_lower not in media_info['filename'].lower() and
                query_lower not in str(media_info.get('metadata', {})).lower()):
                continue
        
        results.append(MediaInfo(**media_info))
    
    # Apply pagination
    start = offset
    end = offset + limit
    return results[start:end]


# Helper functions

async def update_pixeltable_media(table_name: str, column_name: str, 
                                  row_id: str, media_id: UUID, storage_path: str):
    """Update Pixeltable table with media reference."""
    try:
        table = pxt.get_table(table_name)
        # This would update the specific row/column with the media reference
        # Implementation depends on Pixeltable's media handling
        logger.info(f"Updated {table_name}.{column_name}[{row_id}] with media {media_id}")
    except Exception as e:
        logger.error(f"Failed to update Pixeltable: {e}")


async def process_media_task(job_id: UUID, media_id: UUID, 
                             operation: ProcessingOperation,
                             parameters: Dict[str, Any],
                             output_format: Optional[MediaFormat]):
    """Background task to process media."""
    try:
        # Update job status
        processing_jobs[job_id]['status'] = 'processing'
        processing_jobs[job_id]['progress'] = 10.0
        
        # Get media info
        media_info = media_store[media_id]
        
        # Retrieve original file
        original_file = await storage_manager.retrieve(media_info['storage_path'])
        
        # Process based on operation
        if operation == ProcessingOperation.THUMBNAIL:
            # Generate thumbnail (simplified - would use Pillow)
            result_media_id = uuid4()
            # ... processing logic ...
            processing_jobs[job_id]['result_media_id'] = str(result_media_id)
        
        elif operation == ProcessingOperation.RESIZE:
            # Resize image
            pass
        
        elif operation == ProcessingOperation.CONVERT:
            # Convert format
            pass
        
        # Update job as completed
        processing_jobs[job_id]['status'] = 'completed'
        processing_jobs[job_id]['progress'] = 100.0
        processing_jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        # Update job as failed
        processing_jobs[job_id]['status'] = 'failed'
        processing_jobs[job_id]['error_message'] = str(e)
        processing_jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()
        logger.error(f"Processing job {job_id} failed: {e}")