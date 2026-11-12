
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class AudienceCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=20)
    age: int | None = Field(default=None, ge=0, le=120)
    gender: str | None = Field(default=None, max_length=30)
    occupation: str | None = Field(default=None, max_length=100)
    preferred_language: str | None = Field(default=None, max_length=50)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_contact_details(self):
        if not self.email and not self.phone_number:
            raise ValueError(
                "At least one contact method (email or phone number) is required"
            )
        return self


class AudienceUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=20)
    age: int | None = Field(default=None, ge=0, le=120)
    gender: str | None = Field(default=None, max_length=30)
    occupation: str | None = Field(default=None, max_length=100)
    preferred_language: str | None = Field(default=None, max_length=50)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class AudienceResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr | None
    phone_number: str | None
    age: int | None
    gender: str | None
    occupation: str | None
    preferred_language: str | None
    state: str | None
    city: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
