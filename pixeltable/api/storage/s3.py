"""S3-compatible storage backend."""

import io
from typing import BinaryIO, Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from .base import StorageBackend

logger = logging.getLogger(__name__)

# Note: boto3 is optional and should be installed separately
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    logger.warning("boto3 not installed. S3 storage backend will not be available.")


class S3StorageBackend(StorageBackend):
    """S3-compatible storage backend implementation."""
    
    def __init__(self, bucket: str, region: str = 'us-east-1',
                 access_key: Optional[str] = None, secret_key: Optional[str] = None,
                 endpoint_url: Optional[str] = None, public_base_url: Optional[str] = None):
        """Initialize S3 storage backend."""
        if not HAS_BOTO3:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
        
        self.bucket = bucket
        self.region = region
        self.public_base_url = public_base_url
        
        # Create S3 client
        client_kwargs = {
            'region_name': region,
        }
        
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url
        
        if access_key and secret_key:
            client_kwargs['aws_access_key_id'] = access_key
            client_kwargs['aws_secret_access_key'] = secret_key
        
        self.s3_client = boto3.client('s3', **client_kwargs)
        
        # Ensure bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Try to create bucket
                try:
                    if region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=bucket)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=bucket,
                            CreateBucketConfiguration={'LocationConstraint': region}
                        )
                    logger.info(f"Created S3 bucket: {bucket}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                raise
    
    async def store(self, file: BinaryIO, key: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a file in S3."""
        try:
            file.seek(0)
            
            # Prepare metadata for S3
            s3_metadata = {}
            if metadata:
                # S3 metadata must be strings
                s3_metadata = {k: str(v) for k, v in metadata.items()}
            
            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket,
                key,
                ExtraArgs={'Metadata': s3_metadata} if s3_metadata else None
            )
            
            return key
        except ClientError as e:
            logger.error(f"Failed to store file in S3: {e}")
            raise
    
    async def retrieve(self, key: str) -> BinaryIO:
        """Retrieve a file from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read()
            return io.BytesIO(content)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {key}")
            logger.error(f"Failed to retrieve file from S3: {e}")
            raise
    
    async def delete(self, key: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False
            logger.error(f"Failed to delete file from S3: {e}")
            raise
    
    async def exists(self, key: str) -> bool:
        """Check if a file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Failed to check file existence in S3: {e}")
            raise
    
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a presigned URL for the file."""
        if self.public_base_url and not expires_in:
            # Return public URL if configured
            return f"{self.public_base_url.rstrip('/')}/{key}"
        
        try:
            # Generate presigned URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in or 3600  # Default 1 hour
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    async def get_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for a file in S3."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=key)
            
            metadata = {
                'size': response['ContentLength'],
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'etag': response.get('ETag', '').strip('"'),
                'last_modified': response['LastModified'].isoformat() if 'LastModified' in response else None,
            }
            
            # Add custom metadata
            if 'Metadata' in response:
                metadata['custom_metadata'] = response['Metadata']
            
            return metadata
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise FileNotFoundError(f"File not found: {key}")
            logger.error(f"Failed to get metadata from S3: {e}")
            raise
    
    async def list_files(self, prefix: Optional[str] = None, limit: int = 100) -> List[str]:
        """List files in S3 with optional prefix filter."""
        try:
            params = {
                'Bucket': self.bucket,
                'MaxKeys': limit,
            }
            
            if prefix:
                params['Prefix'] = prefix
            
            response = self.s3_client.list_objects_v2(**params)
            
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            
            return files
        except ClientError as e:
            logger.error(f"Failed to list files in S3: {e}")
            raise
    
    async def get_size(self, key: str) -> int:
        """Get the size of a file in S3."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return response['ContentLength']
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise FileNotFoundError(f"File not found: {key}")
            logger.error(f"Failed to get file size from S3: {e}")
            raise
    
    def generate_upload_url(self, key: str, expires_in: int = 3600, 
                           content_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate a presigned URL for direct upload to S3."""
        try:
            conditions = []
            fields = {}
            
            if content_type:
                conditions.append({"Content-Type": content_type})
                fields["Content-Type"] = content_type
            
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket,
                Key=key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expires_in
            )
            
            return response
        except ClientError as e:
            logger.error(f"Failed to generate upload URL: {e}")
            raise