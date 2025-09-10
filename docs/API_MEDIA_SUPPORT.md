# Pixeltable API Media Support Documentation

## Overview

The Pixeltable API provides comprehensive media management capabilities, allowing you to upload, process, search, and manage various types of media files including images, videos, audio files, and documents.

## Key Features

- **Multi-format Support**: Handle images, videos, audio, and documents
- **Direct Upload & URL Ingestion**: Upload files directly or ingest from URLs
- **Processing Operations**: Thumbnail generation, resizing, format conversion, and more
- **Storage Abstraction**: Support for local filesystem and S3-compatible storage
- **Search & Discovery**: Query media by type, format, metadata, and more
- **Table Integration**: Link media files to specific table columns and rows

## Media Types and Formats

### Supported Media Types
- `image`: Photos, graphics, and visual content
- `video`: Movies, clips, and animations
- `audio`: Music, podcasts, and sound files
- `document`: PDFs, text files, spreadsheets, and other documents
- `other`: Unrecognized or specialized formats

### Supported Formats
- **Images**: JPEG, PNG, GIF, WebP, SVG
- **Videos**: MP4, WebM, AVI, MOV
- **Audio**: MP3, WAV, OGG, AAC
- **Documents**: PDF, TXT, DOC/DOCX, XLS/XLSX, CSV, JSON, XML, HTML, Markdown

## API Endpoints

### Upload Media

**POST** `/api/v1/media/upload`

Upload a media file with optional metadata and table references.

```bash
curl -X POST http://localhost:8000/api/v1/media/upload \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/image.jpg" \
  -F 'metadata={"tags":["product","hero"]}' \
  -F "table_name=products" \
  -F "column_name=hero_image" \
  -F "row_id=123"
```

**Response:**
```json
{
  "media_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "image.jpg",
  "media_type": "image",
  "format": "jpeg",
  "size_bytes": 102400,
  "url": "https://storage.example.com/media/550e8400-e29b-41d4-a716-446655440000.jpg",
  "storage_path": "media/550e8400-e29b-41d4-a716-446655440000.jpg",
  "storage_backend": "s3",
  "metadata": {
    "width": 1920,
    "height": 1080,
    "tags": ["product", "hero"]
  },
  "table_name": "products",
  "column_name": "hero_image",
  "row_id": "123",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Ingest from URL

**POST** `/api/v1/media/ingest`

Ingest media from a remote URL.

```json
{
  "url": "https://example.com/video.mp4",
  "filename": "training-video.mp4",
  "metadata": {
    "source": "youtube",
    "category": "tutorial"
  }
}
```

### Get Media Info

**GET** `/api/v1/media/{media_id}`

Retrieve metadata and information about a specific media file.

### Download Media

**GET** `/api/v1/media/{media_id}/download`

Download the original media file.

### Delete Media

**DELETE** `/api/v1/media/{media_id}`

Remove a media file from storage.

### Search Media

**GET** `/api/v1/media/search`

Search for media files with various filters.

**Query Parameters:**
- `query`: Text search query
- `media_type`: Filter by media type
- `format`: Filter by file format
- `min_size`: Minimum file size in bytes
- `max_size`: Maximum file size in bytes
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date
- `table_name`: Filter by associated table
- `column_name`: Filter by associated column
- `limit`: Maximum results (default: 50)
- `offset`: Pagination offset

**Example:**
```bash
curl "http://localhost:8000/api/v1/media/search?media_type=image&format=jpeg&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Processing Operations

### Create Processing Job

**POST** `/api/v1/media/{media_id}/process`

Create a background job to process media.

**Available Operations:**
- `thumbnail`: Generate a thumbnail image
- `resize`: Resize to specific dimensions
- `convert`: Convert to different format
- `compress`: Reduce file size
- `extract_metadata`: Extract detailed metadata
- `extract_text`: Extract text from documents
- `extract_audio`: Extract audio from video
- `extract_frames`: Extract frames from video
- `transcode`: Transcode video/audio

**Example - Generate Thumbnail:**
```json
{
  "operation": "thumbnail",
  "parameters": {
    "width": 256,
    "height": 256,
    "maintain_aspect": true
  }
}
```

**Example - Resize Image:**
```json
{
  "operation": "resize",
  "parameters": {
    "width": 1280,
    "height": 720,
    "quality": 85
  }
}
```

**Example - Convert Format:**
```json
{
  "operation": "convert",
  "output_format": "webp",
  "parameters": {
    "quality": 90
  }
}
```

### Get Processing Job Status

**GET** `/api/v1/media/jobs/{job_id}`

Check the status of a processing job.

**Response:**
```json
{
  "job_id": "abc123",
  "media_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation": "thumbnail",
  "status": "completed",
  "progress": 100,
  "result": {
    "output_media_id": "660e8400-e29b-41d4-a716-446655441111",
    "output_url": "https://storage.example.com/thumbnails/..."
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

### List Processing Jobs

**GET** `/api/v1/media/jobs`

List all processing jobs with optional filters.

**Query Parameters:**
- `media_id`: Filter by source media
- `status`: Filter by job status

### Cancel Processing Job

**POST** `/api/v1/media/jobs/{job_id}/cancel`

Cancel a pending or running processing job.

## SDK Usage Examples

### JavaScript/TypeScript

```typescript
import PixeltableClient from '@a24z/pixeltable-sdk';

const client = new PixeltableClient({
  baseUrl: 'http://localhost:8000/api/v1',
  apiKey: 'YOUR_API_KEY'
});

// Upload a file
const file = new File(['content'], 'document.pdf', { type: 'application/pdf' });
const media = await client.uploadMedia(file, {
  metadata: { category: 'reports' },
  table_name: 'documents',
  column_name: 'file',
  row_id: '123'
});

// Search for images
const images = await client.searchMedia({
  media_type: 'image',
  format: 'jpeg',
  limit: 20
});

// Process media - generate thumbnail
const job = await client.processMedia(media.media_id, {
  operation: 'thumbnail',
  parameters: {
    width: 128,
    height: 128
  }
});

// Check job status
const status = await client.getProcessingJob(job.job_id);
console.log(`Job status: ${status.status}, Progress: ${status.progress}%`);

// Download media
const blob = await client.downloadMedia(media.media_id);
```

### Python (using requests)

```python
import requests

api_url = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

# Upload file
with open("image.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "metadata": '{"tags": ["product"]}',
        "table_name": "products"
    }
    response = requests.post(
        f"{api_url}/media/upload",
        headers=headers,
        files=files,
        data=data
    )
    media = response.json()

# Search media
params = {
    "media_type": "video",
    "limit": 10
}
response = requests.get(
    f"{api_url}/media/search",
    headers=headers,
    params=params
)
videos = response.json()

# Process media
process_request = {
    "operation": "convert",
    "output_format": "webp"
}
response = requests.post(
    f"{api_url}/media/{media['media_id']}/process",
    headers=headers,
    json=process_request
)
job = response.json()
```

## Storage Configuration

The media API supports multiple storage backends:

### Local Storage
Files are stored on the local filesystem. Suitable for development and small deployments.

### S3 Storage
Files are stored in Amazon S3 or S3-compatible storage (MinIO, etc.). Recommended for production deployments.

**Environment Variables:**
```bash
STORAGE_BACKEND=s3
S3_BUCKET=pixeltable-media
S3_REGION=us-east-1
S3_ACCESS_KEY=YOUR_ACCESS_KEY
S3_SECRET_KEY=YOUR_SECRET_KEY
S3_ENDPOINT_URL=https://s3.amazonaws.com  # Optional for S3-compatible services
S3_PUBLIC_BASE_URL=https://cdn.example.com  # Optional CDN URL
```

## Best Practices

1. **File Size Limits**: Configure appropriate file size limits based on your infrastructure
2. **Format Validation**: Always validate file formats before processing
3. **Async Processing**: Use background jobs for time-intensive operations
4. **Caching**: Implement caching for frequently accessed media
5. **CDN Integration**: Use a CDN for serving media files at scale
6. **Cleanup**: Implement retention policies for temporary/processed files
7. **Security**: Use presigned URLs for secure, time-limited access
8. **Monitoring**: Track storage usage and processing job metrics

## Error Handling

Common error responses:

- **400 Bad Request**: Invalid file format or parameters
- **403 Forbidden**: Insufficient permissions for media operations
- **404 Not Found**: Media file or job not found
- **413 Payload Too Large**: File exceeds size limit
- **415 Unsupported Media Type**: File format not supported
- **500 Internal Server Error**: Processing or storage error

## Rate Limits

Media operations have specific rate limits:
- Upload: 100 files per hour per API key
- Processing: 50 jobs per hour per API key
- Download: 1000 requests per hour per API key

## Integration with Pixeltable Tables

Media files can be directly associated with table columns:

1. Define a column type that accepts media references
2. Upload media with table/column/row references
3. Query media associated with specific table data
4. Automatic cleanup when rows are deleted

This tight integration enables powerful workflows for managing media alongside structured data.