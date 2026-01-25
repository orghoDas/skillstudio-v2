from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_instructor
from app.models.user import User
from app.models.course import Course, Module, Lesson
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListResponse, ModuleCreate, ModuleUpdate, ModuleResponse, LessonCreate, LessonUpdate, LessonResponse


router = APIRouter()


# course endpoints
