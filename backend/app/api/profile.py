from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.learner_profile import LearnerProfile
from app.schemas.profile import LearnerProfileResponse, LearnerProfileUpdate


router = APIRouter()


@router.get("/me", response_model=LearnerProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    
    # get my learner profile
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        # create a profile in doesnt exist
        profile = LearnerProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile


@router.put("/me", response_model=LearnerProfileResponse)
async def update_my_profile(
    profile_update: LearnerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    
    # update my learner profile
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        profile = LearnerProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return profile


