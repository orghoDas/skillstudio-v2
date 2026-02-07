"""AWS S3 service for file and video uploads"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import os
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """Service for managing file uploads to AWS S3"""
    
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "skillstudio-uploads")
        
        if not self.aws_access_key or not self.aws_secret_key:
            logger.warning("AWS credentials not configured. File uploads will fail.")
            self.s3_client = None
        else:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename with UUID"""
        ext = Path(original_filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        return unique_name
    
    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        folder: str = "uploads",
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload a file to S3
        
        Args:
            file: File object to upload
            filename: Original filename
            folder: S3 folder/prefix (e.g., 'videos', 'documents', 'images')
            content_type: MIME type of the file
        
        Returns:
            Public URL of uploaded file or None if failed
        """
        if not self.s3_client:
            logger.error("S3 client not configured")
            return None
        
        try:
            unique_filename = self._generate_unique_filename(filename)
            s3_key = f"{folder}/{unique_filename}"
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Make file publicly readable
            extra_args['ACL'] = 'public-read'
            
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            logger.info(f"File uploaded successfully: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            return None
    
    async def upload_video(
        self,
        file: BinaryIO,
        filename: str
    ) -> Optional[str]:
        """Upload a video file to S3"""
        return await self.upload_file(
            file=file,
            filename=filename,
            folder="videos",
            content_type="video/mp4"
        )
    
    async def upload_image(
        self,
        file: BinaryIO,
        filename: str
    ) -> Optional[str]:
        """Upload an image file to S3"""
        # Detect content type based on extension
        ext = Path(filename).suffix.lower()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        content_type = content_type_map.get(ext, 'image/jpeg')
        
        return await self.upload_file(
            file=file,
            filename=filename,
            folder="images",
            content_type=content_type
        )
    
    async def upload_document(
        self,
        file: BinaryIO,
        filename: str
    ) -> Optional[str]:
        """Upload a document file to S3"""
        ext = Path(filename).suffix.lower()
        content_type_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.zip': 'application/zip'
        }
        content_type = content_type_map.get(ext, 'application/octet-stream')
        
        return await self.upload_file(
            file=file,
            filename=filename,
            folder="documents",
            content_type=content_type
        )
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete a file from S3 using its URL"""
        if not self.s3_client:
            logger.error("S3 client not configured")
            return False
        
        try:
            # Extract S3 key from URL
            s3_key = file_url.split(f"{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/")[1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"File deleted successfully: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    async def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for downloading a file
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Presigned URL or None if failed
        """
        if not self.s3_client:
            logger.error("S3 client not configured")
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
    
    async def get_video_metadata(self, video_url: str) -> Optional[dict]:
        """Get metadata for a video file"""
        if not self.s3_client:
            return None
        
        try:
            s3_key = video_url.split(f"{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/")[1]
            
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            logger.error(f"Error getting video metadata: {e}")
            return None


# Global S3 service instance
s3_service = S3Service()
