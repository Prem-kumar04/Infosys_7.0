
from datetime import datetime

from pydantic import BaseModel, Field


class AudienceSegmentCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str | None = None
    filters: dict[str, str] = Field(min_length=1)


class AudienceSegmentResponse(BaseModel):
    id: int
    name: str
    description: str | None
    filters: dict[str, str]
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
