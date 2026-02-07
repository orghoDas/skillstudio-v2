"""File upload endpoints for videos, images, and documents"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_instructor
from app.models.user import User
from app.services.s3_service import s3_service
from app.schemas.upload import UploadResponse, FileType

router = APIRouter(prefix="/upload", tags=["File Upload"])
logger = logging.getLogger(__name__)


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a video file (Instructors only)
    
    - Supported formats: MP4, AVI, MOV, MKV
    - Maximum size: 500MB (configured via server)
    """
    # Validate file type
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    file_ext = file.filename.lower().split('.')[-1]
    
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Upload to S3
        file_url = await s3_service.upload_video(
            file=file.file,
            filename=file.filename
        )
        
        if not file_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload video. Please try again."
            )
        
        logger.info(f"Video uploaded by user {current_user.id}: {file_url}")
        
        return UploadResponse(
            url=file_url,
            filename=file.filename,
            file_type=FileType.VIDEO,
            size=file.size if hasattr(file, 'size') else None
        )
        
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an image file
    
    - Supported formats: JPG, PNG, GIF, WEBP
    - Maximum size: 5MB
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_ext = file.filename.lower().split('.')[-1]
    
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        file_url = await s3_service.upload_image(
            file=file.file,
            filename=file.filename
        )
        
        if not file_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload image. Please try again."
            )
        
        logger.info(f"Image uploaded by user {current_user.id}: {file_url}")
        
        return UploadResponse(
            url=file_url,
            filename=file.filename,
            file_type=FileType.IMAGE,
            size=file.size if hasattr(file, 'size') else None
        )
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/document", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document file (Instructors only)
    
    - Supported formats: PDF, DOC, DOCX, ZIP
    - Maximum size: 20MB
    """
    allowed_extensions = ['.pdf', '.doc', '.docx', '.zip', '.ppt', '.pptx']
    file_ext = file.filename.lower().split('.')[-1]
    
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        file_url = await s3_service.upload_document(
            file=file.file,
            filename=file.filename
        )
        
        if not file_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload document. Please try again."
            )
        
        logger.info(f"Document uploaded by user {current_user.id}: {file_url}")
        
        return UploadResponse(
            url=file_url,
            filename=file.filename,
            file_type=FileType.DOCUMENT,
            size=file.size if hasattr(file, 'size') else None
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/batch", response_model=List[UploadResponse])
async def upload_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files at once (Instructors only)
    
    - Maximum 10 files per batch
    - Mixed file types supported
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per batch"
        )
    
    results = []
    
    for file in files:
        try:
            file_ext = file.filename.lower().split('.')[-1]
            
            # Determine file type and upload
            if f'.{file_ext}' in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                file_url = await s3_service.upload_video(file.file, file.filename)
                file_type = FileType.VIDEO
            elif f'.{file_ext}' in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                file_url = await s3_service.upload_image(file.file, file.filename)
                file_type = FileType.IMAGE
            elif f'.{file_ext}' in ['.pdf', '.doc', '.docx', '.zip']:
                file_url = await s3_service.upload_document(file.file, file.filename)
                file_type = FileType.DOCUMENT
            else:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue
            
            if file_url:
                results.append(UploadResponse(
                    url=file_url,
                    filename=file.filename,
                    file_type=file_type,
                    size=file.size if hasattr(file, 'size') else None
                ))
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            continue
    
    if not results:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload any files"
        )
    
    return results


@router.delete("/{file_type}/{filename}")
async def delete_file(
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Delete an uploaded file (Instructors only)"""
    try:
        # Construct file URL
        file_url = f"https://{s3_service.bucket_name}.s3.{s3_service.aws_region}.amazonaws.com/{file_type}s/{filename}"
        
        success = await s3_service.delete_file(file_url)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete file"
            )
        
        logger.info(f"File deleted by user {current_user.id}: {file_url}")
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Delete failed")
