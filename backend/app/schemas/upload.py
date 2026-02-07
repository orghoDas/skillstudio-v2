"""Pydantic schemas for file uploads"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class FileType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"


class UploadResponse(BaseModel):
    url: str
    filename: str
    file_type: FileType
    size: Optional[int] = None
    
    class Config:
        from_attributes = True


class VideoMetadata(BaseModel):
    duration: Optional[int] = None  # in seconds
    resolution: Optional[str] = None  # e.g., "1920x1080"
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    size: Optional[int] = None
