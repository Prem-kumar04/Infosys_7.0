
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    UserUpdateRequest,
    PasswordChangeRequest,
)


async def update_user_profile(
    current_user: User,
    user_data: UserUpdateRequest,
    db: AsyncSession,
) -> User:
    # Get only the fields supplied by the user
    update_data = user_data.model_dump(exclude_unset=True)

    # Check whether the new email is already registered
    if "email" in update_data and update_data["email"] is not None:
        result = await db.execute(
            select(User).where(
                User.email == update_data["email"],
                User.id != current_user.id,
            )
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email is already registered")

    # Update allowed profile fields
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


async def change_user_password(
    current_user: User,
    password_data: PasswordChangeRequest,
    db: AsyncSession,
) -> None:
    # Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password,
    ):
        raise ValueError("Current password is incorrect")

    # Prevent using the same password again
    if verify_password(
        password_data.new_password,
        current_user.hashed_password,
    ):
        raise ValueError("New password must be different")

    # Hash and save the new password
    current_user.hashed_password = hash_password(
        password_data.new_password
    )

    await db.commit()
