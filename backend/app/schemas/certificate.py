"""Pydantic schemas for certificates"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CertificateRequest(BaseModel):
    enrollment_id: str


class CertificateResponse(BaseModel):
    certificate_id: str
    certificate_url: str
    student_name: str
    course_title: str
    issued_date: datetime
    
    class Config:
        from_attributes = True


class CertificateVerification(BaseModel):
    valid: bool
    certificate_id: str
    student_name: str
    course_title: str
    completion_date: datetime
    issued_by: str
