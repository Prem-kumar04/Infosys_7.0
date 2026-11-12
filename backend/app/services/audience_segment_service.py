
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audience_segment import AudienceSegment
from app.schemas.audience_segment import AudienceSegmentCreate


async def create_audience_segment(
    segment_data: AudienceSegmentCreate,
    user_id: int,
    db: AsyncSession,
) -> AudienceSegment:

    new_segment = AudienceSegment(
        name=segment_data.name,
        description=segment_data.description,
        filters=segment_data.filters,
        created_by=user_id,
    )

    db.add(new_segment)
    await db.commit()
    await db.refresh(new_segment)

    return new_segment


async def get_my_audience_segments(
    user_id: int,
    db: AsyncSession,
) -> list[AudienceSegment]:

    result = await db.execute(
        select(AudienceSegment)
        .where(AudienceSegment.created_by == user_id)
        .order_by(AudienceSegment.id.desc())
    )

    return list(result.scalars().all())


async def get_audience_segment_by_id(
    segment_id: int,
    user_id: int,
    db: AsyncSession,
) -> AudienceSegment | None:

    result = await db.execute(
        select(AudienceSegment).where(
            AudienceSegment.id == segment_id,
            AudienceSegment.created_by == user_id,
        )
    )

    return result.scalar_one_or_none()


async def delete_audience_segment(
    segment: AudienceSegment,
    db: AsyncSession,
) -> None:

    await db.delete(segment)
    await db.commit()
