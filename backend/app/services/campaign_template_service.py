from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign_template import CampaignTemplate
from app.schemas.campaign_template import (
    CampaignTemplateCreate,
    CampaignTemplateUpdate,
)


async def create_template(
    template_data: CampaignTemplateCreate,
    user_id: int,
    db: AsyncSession,
) -> CampaignTemplate:
    template = CampaignTemplate(
        **template_data.model_dump(),
        created_by=user_id,
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return template


async def get_all_templates(
    db: AsyncSession,
) -> list[CampaignTemplate]:
    result = await db.execute(
        select(CampaignTemplate).order_by(CampaignTemplate.created_at.desc())
    )

    return list(result.scalars().all())


async def get_template_by_id(
    template_id: int,
    db: AsyncSession,
) -> CampaignTemplate | None:
    result = await db.execute(
        select(CampaignTemplate).where(
            CampaignTemplate.id == template_id
        )
    )

    return result.scalar_one_or_none()


async def update_template(
    template: CampaignTemplate,
    template_data: CampaignTemplateUpdate,
    db: AsyncSession,
) -> CampaignTemplate:
    update_data = template_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    return template


async def delete_template(
    template: CampaignTemplate,
    db: AsyncSession,
) -> None:
    await db.delete(template)
    await db.commit()