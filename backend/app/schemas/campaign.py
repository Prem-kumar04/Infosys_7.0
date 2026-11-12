
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CampaignCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    objective: str | None = None
    category: str | None = Field(default=None, max_length=100)
    audience_segment_id: int | None = Field(default=None, gt=0)

    template_id: int | None = Field(default=None, gt=0)
    message_subject: str | None = Field(default=None, max_length=255)
    message_content: str | None = None

    scheduled_at: datetime | None = None


class CampaignUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    objective: str | None = None
    category: str | None = Field(default=None, max_length=100)
    audience_segment_id: int | None = Field(default=None, gt=0)

    template_id: int | None = Field(default=None, gt=0)
    message_subject: str | None = Field(default=None, max_length=255)
    message_content: str | None = None

    scheduled_at: datetime | None = None


class CampaignRejectRequest(BaseModel):
    rejection_reason: str = Field(min_length=10, max_length=1000)

    @field_validator("rejection_reason", mode="before")
    @classmethod
    def validate_rejection_reason(cls, value):
        if not isinstance(value, str):
            raise ValueError("Rejection reason must be text")

        cleaned_value = value.strip()

        if len(cleaned_value) < 10:
            raise ValueError(
                "Rejection reason must contain at least 10 characters"
            )

        if len(cleaned_value) > 1000:
            raise ValueError(
                "Rejection reason cannot exceed 1000 characters"
            )

        return cleaned_value


class CampaignResponse(BaseModel):
    id: int
    title: str
    description: str | None
    objective: str | None
    category: str | None
    audience_segment_id: int | None

    template_id: int | None
    message_subject: str | None
    message_content: str | None

    created_by: int
    scheduled_at: datetime | None

    status: str
    submitted_at: datetime | None

    approved_by: int | None
    approved_at: datetime | None

    rejected_by: int | None
    rejected_at: datetime | None
    rejection_reason: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
