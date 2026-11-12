
from pydantic import BaseModel, EmailStr, Field


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    email: EmailStr | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserListResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role_id: int | None
    is_active: bool

    model_config = {"from_attributes": True}
