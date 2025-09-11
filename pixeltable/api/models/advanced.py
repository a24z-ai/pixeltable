"""Advanced features models for Pixeltable API."""

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


# Computed Columns
class ComputedColumnType(str, Enum):
    """Types of computed columns."""
    EXPRESSION = "expression"  # Simple Python expression
    UDF = "udf"  # User-defined function
    AGGREGATE = "aggregate"  # Aggregation function
    WINDOW = "window"  # Window function


class ComputedColumnDefinition(BaseModel):
    """Definition for a computed column."""
    name: str = Field(..., description="Column name")
    column_type: ComputedColumnType = Field(..., description="Type of computed column")
    expression: str = Field(..., description="Computation expression or function")
    dependencies: List[str] = Field(default_factory=list, description="Column dependencies")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    cache_results: bool = Field(default=False, description="Whether to cache computed results")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Column name cannot be empty")
        if not v.replace('_', '').isalnum():
            raise ValueError("Column name must be alphanumeric with underscores")
        return v


class ComputedColumnInfo(BaseModel):
    """Information about a computed column."""
    name: str
    column_type: ComputedColumnType
    expression: str
    dependencies: List[str]
    parameters: Optional[Dict[str, Any]]
    cache_results: bool
    created_at: datetime
    last_computed: Optional[datetime]
    computation_time_ms: Optional[float]


# User-Defined Functions (UDFs)
class UDFLanguage(str, Enum):
    """Supported UDF languages."""
    PYTHON = "python"
    SQL = "sql"
    JAVASCRIPT = "javascript"


class UDFDefinition(BaseModel):
    """Definition for a user-defined function."""
    name: str = Field(..., description="Function name")
    language: UDFLanguage = Field(..., description="Function language")
    code: str = Field(..., description="Function code")
    parameters: List[Dict[str, str]] = Field(..., description="Parameter definitions")
    return_type: str = Field(..., description="Return type")
    description: Optional[str] = Field(default=None, description="Function description")
    deterministic: bool = Field(default=True, description="Whether function is deterministic")


class UDFInfo(BaseModel):
    """Information about a registered UDF."""
    id: str
    name: str
    language: UDFLanguage
    parameters: List[Dict[str, str]]
    return_type: str
    description: Optional[str]
    deterministic: bool
    created_at: datetime
    updated_at: Optional[datetime]
    usage_count: int


# Batch Operations
class BatchOperationType(str, Enum):
    """Types of batch operations."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"


class BatchOperation(BaseModel):
    """Single operation in a batch."""
    operation: BatchOperationType
    table: str
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    where: Optional[Dict[str, Any]] = None
    set: Optional[Dict[str, Any]] = None


class BatchRequest(BaseModel):
    """Request for batch operations."""
    operations: List[BatchOperation] = Field(..., min_items=1, max_items=1000)
    transaction: bool = Field(default=True, description="Execute in transaction")
    continue_on_error: bool = Field(default=False, description="Continue on error")
    return_results: bool = Field(default=False, description="Return operation results")


class BatchResult(BaseModel):
    """Result of batch operations."""
    total_operations: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    results: Optional[List[Any]] = None
    execution_time_ms: float


# Async Jobs
class JobType(str, Enum):
    """Types of async jobs."""
    DATA_IMPORT = "data_import"
    DATA_EXPORT = "data_export"
    BATCH_OPERATION = "batch_operation"
    MEDIA_PROCESSING = "media_processing"
    TABLE_RECOMPUTE = "table_recompute"
    CUSTOM = "custom"


class JobStatus(str, Enum):
    """Status of async jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobRequest(BaseModel):
    """Request to create an async job."""
    job_type: JobType
    parameters: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")
    webhook_url: Optional[str] = None
    webhook_events: List[str] = Field(default_factory=lambda: ["completed", "failed"])
    timeout_seconds: Optional[int] = Field(default=3600, description="Job timeout")


class JobInfo(BaseModel):
    """Information about an async job."""
    job_id: str
    job_type: JobType
    status: JobStatus
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    webhook_url: Optional[str] = None
    logs: List[str] = Field(default_factory=list)


# Webhooks
class WebhookEvent(str, Enum):
    """Types of webhook events."""
    JOB_STARTED = "job.started"
    JOB_PROGRESS = "job.progress"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    TABLE_CREATED = "table.created"
    TABLE_UPDATED = "table.updated"
    TABLE_DELETED = "table.deleted"
    DATA_INSERTED = "data.inserted"
    DATA_UPDATED = "data.updated"
    DATA_DELETED = "data.deleted"
    MEDIA_UPLOADED = "media.uploaded"
    MEDIA_PROCESSED = "media.processed"


class WebhookConfig(BaseModel):
    """Configuration for a webhook."""
    url: str = Field(..., description="Webhook endpoint URL")
    events: List[WebhookEvent] = Field(..., description="Events to subscribe to")
    active: bool = Field(default=True, description="Whether webhook is active")
    secret: Optional[str] = Field(default=None, description="Secret for HMAC validation")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Custom headers")
    retry_config: Optional[Dict[str, Any]] = Field(default=None, description="Retry configuration")


class WebhookInfo(BaseModel):
    """Information about a registered webhook."""
    webhook_id: str
    url: str
    events: List[WebhookEvent]
    active: bool
    created_at: datetime
    last_triggered: Optional[datetime]
    success_count: int
    failure_count: int


class WebhookPayload(BaseModel):
    """Payload sent to webhook endpoints."""
    webhook_id: str
    event: WebhookEvent
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None


# Import/Export
class ImportFormat(str, Enum):
    """Supported import formats."""
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    PARQUET = "parquet"
    EXCEL = "excel"


class ExportFormat(str, Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    PARQUET = "parquet"
    EXCEL = "excel"
    LANCE = "lance"


class ImportRequest(BaseModel):
    """Request to import data."""
    table_name: str
    format: ImportFormat
    source_url: Optional[str] = None
    mapping: Optional[Dict[str, str]] = Field(default=None, description="Column mapping")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Format-specific options")
    validation_rules: Optional[Dict[str, Any]] = Field(default=None, description="Validation rules")
    on_error: Literal["skip", "fail", "default"] = Field(default="skip")
    batch_size: int = Field(default=1000, ge=1, le=10000)


class ExportRequest(BaseModel):
    """Request to export data."""
    table_name: str
    format: ExportFormat
    destination_url: Optional[str] = None
    columns: Optional[List[str]] = None
    where: Optional[Dict[str, Any]] = None
    order_by: Optional[List[Dict[str, str]]] = None
    limit: Optional[int] = None
    options: Optional[Dict[str, Any]] = Field(default=None, description="Format-specific options")
    compress: bool = Field(default=False, description="Whether to compress output")


class ImportResult(BaseModel):
    """Result of import operation."""
    job_id: str
    table_name: str
    format: ImportFormat
    rows_processed: int
    rows_imported: int
    rows_skipped: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    duration_seconds: float


class ExportResult(BaseModel):
    """Result of export operation."""
    job_id: str
    table_name: str
    format: ExportFormat
    rows_exported: int
    file_size_bytes: int
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    duration_seconds: float


# Streaming
class StreamConfig(BaseModel):
    """Configuration for streaming operations."""
    chunk_size: int = Field(default=1000, ge=1, le=10000, description="Rows per chunk")
    format: Literal["json", "jsonl", "csv"] = Field(default="jsonl")
    compression: Optional[Literal["gzip", "brotli"]] = None
    include_headers: bool = Field(default=True, description="Include column headers")


class StreamInfo(BaseModel):
    """Information about an active stream."""
    stream_id: str
    table_name: str
    total_rows: Optional[int]
    rows_sent: int
    chunks_sent: int
    created_at: datetime
    last_activity: datetime
    config: StreamConfig