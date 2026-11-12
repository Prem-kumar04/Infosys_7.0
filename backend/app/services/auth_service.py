
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest


async def register_user(
    user_data: RegisterRequest,
    db: AsyncSession,
) -> User:
    # Check whether the email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("Email is already registered")

    # Hash the password before storing it
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
    )

    # Save the user in PostgreSQL
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def login_user(
    email: str,
    password: str,
    db: AsyncSession,
) -> str:
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    # Verify credentials
    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")

    # Check account status
    if not user.is_active:
        raise ValueError("User account is inactive")

    # Generate JWT access token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return access_token
