"""
Video Processing API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.course import Lesson
from app.services.video_processing import VideoProcessingService


router = APIRouter(prefix="/api/video", tags=["Video Processing"])


class VideoUploadInitRequest(BaseModel):
    lesson_id: UUID
    filename: str


class TranscodingStartRequest(BaseModel):
    lesson_id: UUID
    s3_key: str


class VideoWatchTrackingRequest(BaseModel):
    lesson_id: UUID
    watch_duration_seconds: int
    completion_percentage: float
    playback_speed: float = 1.0
    quality_selected: str | None = None
    device_type: str | None = None


@router.post("/upload/init")
async def initiate_video_upload(
    request: VideoUploadInitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Initiate video upload - returns presigned S3 URL
    Only instructors can upload videos for their lessons
    """
    # Verify lesson exists and user owns it
    result = await db.execute(
        select(Lesson).where(Lesson.id == request.lesson_id)
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Verify ownership (lesson -> module -> course -> instructor)
    from app.models.course import Module, Course
    result = await db.execute(
        select(Course)
        .join(Module, Module.course_id == Course.id)
        .join(Lesson, Lesson.module_id == Module.id)
        .where(Lesson.id == request.lesson_id)
    )
    course = result.scalar_one_or_none()
    
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload video for this lesson"
        )
    
    video_service = VideoProcessingService()
    upload_data = await video_service.initiate_video_upload(
        db, request.lesson_id, request.filename
    )
    
    return {
        "success": True,
        "upload_url": upload_data["upload_url"],
        "fields": upload_data["fields"],
        "s3_key": upload_data["s3_key"]
    }


@router.post("/transcode/start")
async def start_video_transcoding(
    request: TranscodingStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start video transcoding job
    """
    # Verify ownership
    from app.models.course import Module, Course
    result = await db.execute(
        select(Course)
        .join(Module, Module.course_id == Course.id)
        .join(Lesson, Lesson.module_id == Module.id)
        .where(Lesson.id == request.lesson_id)
    )
    course = result.scalar_one_or_none()
    
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    video_service = VideoProcessingService()
    job_id = await video_service.start_transcoding(
        db, request.lesson_id, request.s3_key
    )
    
    return {
        "success": True,
        "job_id": job_id,
        "message": "Transcoding started"
    }


@router.get("/transcode/status/{lesson_id}")
async def get_transcoding_status(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check transcoding status
    """
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    if not lesson.transcoding_job_id:
        return {
            "status": lesson.video_status or "not_started",
            "progress": 0
        }
    
    video_service = VideoProcessingService()
    status_data = await video_service.check_transcoding_status(
        db, lesson_id, lesson.transcoding_job_id
    )
    
    return status_data


@router.post("/track-watch")
async def track_video_watch(
    request: VideoWatchTrackingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Track video watch analytics
    """
    video_service = VideoProcessingService()
    await video_service.track_video_watch(
        db,
        lesson_id=request.lesson_id,
        user_id=current_user.id,
        watch_duration_seconds=request.watch_duration_seconds,
        completion_percentage=request.completion_percentage,
        playback_speed=request.playback_speed,
        quality_selected=request.quality_selected,
        device_type=request.device_type
    )
    
    return {"message": "Watch tracked"}


@router.get("/analytics/{lesson_id}")
async def get_video_analytics(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get video analytics (instructor only)
    """
    # Verify ownership
    from app.models.course import Module, Course
    result = await db.execute(
        select(Course)
        .join(Module, Module.course_id == Course.id)
        .join(Lesson, Lesson.module_id == Module.id)
        .where(Lesson.id == lesson_id)
    )
    course = result.scalar_one_or_none()
    
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    video_service = VideoProcessingService()
    analytics = await video_service.get_video_analytics(db, lesson_id)
    
    return analytics
