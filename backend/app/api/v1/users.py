
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_user,
    require_permission,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserUpdateRequest,
    PasswordChangeRequest,
    UserListResponse,
)
from app.services.user_service import (
    update_user_profile,
    change_user_password,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# View own profile
@router.get("/me", response_model=UserListResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


# Update own profile
@router.patch("/me", response_model=UserListResponse)
async def update_my_profile(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_user_profile(
            current_user,
            user_data,
            db,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


# Change own password
@router.patch("/me/password")
async def change_my_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await change_user_password(
            current_user,
            password_data,
            db,
        )

        return {"message": "Password changed successfully"}

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# View all users
@router.get("/", response_model=list[UserListResponse])
async def get_users(
    current_user: User = Depends(
        require_permission("users.read")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.id)
    )

    return result.scalars().all()
