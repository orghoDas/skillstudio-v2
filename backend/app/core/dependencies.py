from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import decode_access_token, verify_token_type
from app.models.user import User, UserRole


# http bearer token scheme
security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.

    usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user}
    """

    token = credentials.credentials


    # decode token
    payload = decode_access_token(token)

    if not payload or not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    user_id : Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    # get user from database
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_active_learner(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is an active learner.
    """

    if current_user.role != UserRole.LEARNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only learners are allowed to access this resource",
        )
    
    return current_user


async def get_current_active_instructor(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is an active instructor.
    """

    if current_user.role != UserRole.INSTRUCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors are allowed to access this resource",
        )
    
    return current_user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active (alias for get_current_user for compatibility).
    """
    return current_user


async def get_current_active_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is an active admin.
    """

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are allowed to access this resource",
        )
    
    return current_user


# Alias for compatibility
get_current_admin = get_current_active_admin


