from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/account-holders", tags=["account-holders"])

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get My Profile",
    description="Retrieves the current authenticated user's profile information.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update My Profile",
    description="Updates the email address of the current user.",
)
async def patch_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    if payload.email is None:
        return current_user
        
    if payload.email == current_user.email:
        return current_user
        
    # Check uniqueness
    result = await session.execute(select(User).where(User.email == payload.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
        
    current_user.email = payload.email
    await session.commit()
    await session.refresh(current_user)
    
    return current_user
