
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audience import Audience
from app.schemas.audience import AudienceCreate, AudienceUpdate


async def create_audience(
    audience_data: AudienceCreate,
    db: AsyncSession,
) -> Audience:
    new_audience = Audience(**audience_data.model_dump())

    db.add(new_audience)
    await db.commit()
    await db.refresh(new_audience)

    return new_audience


async def get_all_audiences(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Audience]:
    result = await db.execute(
        select(Audience)
        .order_by(Audience.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_audience_by_id(
    audience_id: int,
    db: AsyncSession,
) -> Audience | None:
    result = await db.execute(
        select(Audience).where(Audience.id == audience_id)
    )

    return result.scalar_one_or_none()


async def update_audience(
    audience: Audience,
    audience_data: AudienceUpdate,
    db: AsyncSession,
) -> Audience:
    update_data = audience_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(audience, field, value)

    if not audience.email and not audience.phone_number:
        raise ValueError(
            "At least one contact method is required"
        )

    await db.commit()
    await db.refresh(audience)

    return audience


async def delete_audience(
    audience: Audience,
    db: AsyncSession,
) -> None:
    await db.delete(audience)
    await db.commit()


async def filter_audiences(
    db: AsyncSession,
    gender: str | None = None,
    preferred_language: str | None = None,
    state: str | None = None,
    city: str | None = None,
    occupation: str | None = None,
) -> list[Audience]:

    query = select(Audience).where(
        Audience.is_active.is_(True)
    )

    if gender:
        query = query.where(
            Audience.gender.ilike(gender.strip())
        )

    if preferred_language:
        query = query.where(
            Audience.preferred_language.ilike(
                preferred_language.strip()
            )
        )

    if state:
        query = query.where(
            Audience.state.ilike(state.strip())
        )

    if city:
        query = query.where(
            Audience.city.ilike(city.strip())
        )

    if occupation:
        query = query.where(
            Audience.occupation.ilike(occupation.strip())
        )

    query = query.order_by(Audience.id.desc())

    result = await db.execute(query)

    return list(result.scalars().all())
