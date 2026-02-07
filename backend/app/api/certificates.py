"""Certificate generation and management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.course import Course, Enrollment
from app.services.certificate_service import certificate_generator
from app.services.s3_service import s3_service
from app.services.email_service import email_service
from app.schemas.certificate import CertificateRequest, CertificateResponse

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.post("/generate/{enrollment_id}", response_model=CertificateResponse)
async def generate_certificate(
    enrollment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate certificate for completed course"""
    # Get enrollment with course details
    result = await db.execute(
        select(Enrollment, Course)
        .join(Course)
        .where(
            and_(
                Enrollment.id == enrollment_id,
                Enrollment.user_id == current_user.id,
                Enrollment.status == "completed"
            )
        )
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found or course not completed"
        )
    
    enrollment, course = row
    
    # Get instructor details
    instructor_result = await db.execute(
        select(User).where(User.id == course.instructor_id)
    )
    instructor = instructor_result.scalar_one()
    
    # Generate certificate ID
    certificate_id = f"SS-{uuid.uuid4().hex[:8].upper()}"
    
    # Generate PDF
    pdf_buffer = certificate_generator.generate_certificate(
        student_name=current_user.full_name,
        course_title=course.title,
        instructor_name=instructor.full_name,
        completion_date=enrollment.completed_at or datetime.utcnow(),
        course_duration=f"{course.duration_hours or 0} hours",
        certificate_id=certificate_id
    )
    
    # Upload to S3
    filename = f"certificate_{certificate_id}.pdf"
    certificate_url = await s3_service.upload_file(
        file=pdf_buffer,
        filename=filename,
        folder="certificates",
        content_type="application/pdf"
    )
    
    if not certificate_url:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload certificate"
        )
    
    # Update enrollment with certificate URL
    enrollment.certificate_url = certificate_url
    await db.commit()
    
    # Send completion email with certificate
    try:
        await email_service.send_course_completion_email(
            user_email=current_user.email,
            user_name=current_user.full_name,
            course_title=course.title,
            completion_date=enrollment.completed_at.strftime("%B %d, %Y") if enrollment.completed_at else datetime.utcnow().strftime("%B %d, %Y"),
            certificate_url=certificate_url
        )
    except Exception as e:
        print(f"Failed to send completion email: {e}")
    
    return CertificateResponse(
        certificate_id=certificate_id,
        certificate_url=certificate_url,
        student_name=current_user.full_name,
        course_title=course.title,
        issued_date=datetime.utcnow()
    )


@router.get("/download/{enrollment_id}")
async def download_certificate(
    enrollment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download certificate PDF"""
    # Get enrollment
    result = await db.execute(
        select(Enrollment, Course)
        .join(Course)
        .where(
            and_(
                Enrollment.id == enrollment_id,
                Enrollment.user_id == current_user.id,
                Enrollment.status == "completed"
            )
        )
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )
    
    enrollment, course = row
    
    if not enrollment.certificate_url:
        raise HTTPException(
            status_code=404,
            detail="Certificate not yet generated. Generate it first."
        )
    
    # Get instructor
    instructor_result = await db.execute(
        select(User).where(User.id == course.instructor_id)
    )
    instructor = instructor_result.scalar_one()
    
    # Generate fresh PDF
    certificate_id = enrollment.certificate_url.split('_')[-1].replace('.pdf', '')
    
    pdf_buffer = certificate_generator.generate_certificate(
        student_name=current_user.full_name,
        course_title=course.title,
        instructor_name=instructor.full_name,
        completion_date=enrollment.completed_at or datetime.utcnow(),
        course_duration=f"{course.duration_hours or 0} hours",
        certificate_id=certificate_id
    )
    
    # Return as downloadable PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{course.title.replace(' ', '_')}.pdf"
        }
    )


@router.get("/verify/{certificate_id}")
async def verify_certificate(
    certificate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify certificate authenticity"""
    # Search for enrollment with certificate URL containing this ID
    result = await db.execute(
        select(Enrollment, Course, User)
        .join(Course, Enrollment.course_id == Course.id)
        .join(User, Enrollment.user_id == User.id)
        .where(Enrollment.certificate_url.contains(certificate_id))
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )
    
    enrollment, course, user = row
    
    return {
        "valid": True,
        "certificate_id": certificate_id,
        "student_name": user.full_name,
        "course_title": course.title,
        "completion_date": enrollment.completed_at,
        "issued_by": "SkillStudio"
    }
