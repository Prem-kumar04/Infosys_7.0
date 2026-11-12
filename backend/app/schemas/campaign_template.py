from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CampaignTemplateCreate(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    description: str | None = None
    category: str = Field(min_length=2, max_length=100)
    language: str = Field(min_length=2, max_length=50)
    subject: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=1)


class CampaignTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    language: str | None = Field(default=None, min_length=2, max_length=50)
    subject: str | None = Field(default=None, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None


class CampaignTemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str
    language: str
    subject: str | None
    content: str
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)