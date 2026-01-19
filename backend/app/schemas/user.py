from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


# request schemas
class UserCreate(BaseModel):
    # schema for user registration
    email : EmailStr
    password : str = Field(..., min_length=8, max_length=128)
    full_name : str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.LEARNER

    @validator('password')
    def password_strength(cls, v):
        # validate password strength
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v
    
    @validator('full_name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty or whitespace')
        return v.strip()
    

class UserLogin(BaseModel):
    # schema for user login
    email : EmailStr
    password : str


class UserUpdate(BaseModel):
    # schema for updating user info
    full_name : Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None

    @validator('full_name')
    def name_not_empty(cls, v):
        if v and not v.strip():
            raise ValueError('Full name cannot be empty or whitespace')
        return v.strip() if v else v
    

# response schemas
class UserResponse(BaseModel):
    # schema for user data in responses
    id : UUID
    email : EmailStr
    full_name : str
    role: UserRole
    is_active : bool
    email_verified : bool
    created_at : datetime
    last_login : Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    # schema for JWT token response
    access_token : str
    refresh_token : str
    token_type : str = "bearer"
    expires_in : int  # seconds until expiration
    user : UserResponse


class TokenDateils(BaseModel):
    # schema for decoded token details
    user_id : UUID
    email : EmailStr
    role: UserRole