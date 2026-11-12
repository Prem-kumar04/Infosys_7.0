
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.audience_segment import (
    AudienceSegmentCreate,
    AudienceSegmentResponse,
)
from app.services.audience_segment_service import (
    create_audience_segment,
    delete_audience_segment,
    get_audience_segment_by_id,
    get_my_audience_segments,
)

router = APIRouter(
    prefix="/audience-segments",
    tags=["Saved Audience Segments"],
)


@router.post(
    "/",
    response_model=AudienceSegmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_segment_endpoint(
    segment_data: AudienceSegmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.create")),
):
    try:
        return await create_audience_segment(
            segment_data=segment_data,
            user_id=current_user.id,
            db=db,
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="You already have a segment with this name",
        )


@router.get(
    "/",
    response_model=list[AudienceSegmentResponse],
)
async def list_segments_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.read")),
):
    return await get_my_audience_segments(
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/{segment_id}",
    response_model=AudienceSegmentResponse,
)
async def get_segment_endpoint(
    segment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.read")),
):
    segment = await get_audience_segment_by_id(
        segment_id=segment_id,
        user_id=current_user.id,
        db=db,
    )

    if segment is None:
        raise HTTPException(
            status_code=404,
            detail="Audience segment not found",
        )

    return segment


@router.delete(
    "/{segment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_segment_endpoint(
    segment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.update")),
):
    segment = await get_audience_segment_by_id(
        segment_id=segment_id,
        user_id=current_user.id,
        db=db,
    )

    if segment is None:
        raise HTTPException(
            status_code=404,
            detail="Audience segment not found",
        )

    await delete_audience_segment(segment, db)
    return None
