
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.models.audience_segment import AudienceSegment
from app.models.campaign_template import CampaignTemplate
from app.schemas.campaign import CampaignCreate, CampaignUpdate


async def validate_audience_segment(
    segment_id: int,
    user_id: int,
    db: AsyncSession,
) -> AudienceSegment:
    result = await db.execute(
        select(AudienceSegment).where(
            AudienceSegment.id == segment_id,
            AudienceSegment.created_by == user_id,
        )
    )

    segment = result.scalar_one_or_none()

    if segment is None:
        raise ValueError(
            "Selected audience segment was not found "
            "or does not belong to you"
        )

    return segment


async def get_active_template(
    template_id: int,
    db: AsyncSession,
) -> CampaignTemplate:
    result = await db.execute(
        select(CampaignTemplate).where(
            CampaignTemplate.id == template_id,
            CampaignTemplate.is_active.is_(True),
        )
    )

    template = result.scalar_one_or_none()

    if template is None:
        raise ValueError(
            "Selected campaign template was not found or is inactive"
        )

    return template


async def create_campaign(
    campaign_data: CampaignCreate,
    user_id: int,
    db: AsyncSession,
) -> Campaign:

    campaign_values = campaign_data.model_dump()

    if campaign_values["audience_segment_id"] is not None:
        await validate_audience_segment(
            campaign_values["audience_segment_id"],
            user_id,
            db,
        )

    template_id = campaign_values["template_id"]

    if template_id is not None:
        template = await get_active_template(template_id, db)

        if campaign_values["message_subject"] is None:
            campaign_values["message_subject"] = template.subject

        if campaign_values["message_content"] is None:
            campaign_values["message_content"] = template.content

    new_campaign = Campaign(
        **campaign_values,
        created_by=user_id,
        status="draft",
    )

    db.add(new_campaign)
    await db.commit()
    await db.refresh(new_campaign)

    return new_campaign


async def get_my_campaigns(
    user_id: int,
    db: AsyncSession,
) -> list[Campaign]:
    result = await db.execute(
        select(Campaign)
        .where(Campaign.created_by == user_id)
        .order_by(Campaign.id.desc())
    )

    return list(result.scalars().all())


async def get_campaign_by_id(
    campaign_id: int,
    user_id: int,
    db: AsyncSession,
) -> Campaign | None:
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.created_by == user_id,
        )
    )

    return result.scalar_one_or_none()


async def update_campaign(
    campaign: Campaign,
    campaign_data: CampaignUpdate,
    db: AsyncSession,
) -> Campaign:

    if campaign.status != "draft":
        raise ValueError("Only draft campaigns can be edited")

    update_data = campaign_data.model_dump(exclude_unset=True)

    if (
        "audience_segment_id" in update_data
        and update_data["audience_segment_id"] is not None
    ):
        await validate_audience_segment(
            update_data["audience_segment_id"],
            campaign.created_by,
            db,
        )

    if (
        "template_id" in update_data
        and update_data["template_id"] is not None
    ):
        template = await get_active_template(
            update_data["template_id"],
            db,
        )

        if "message_subject" not in update_data:
            update_data["message_subject"] = template.subject

        if "message_content" not in update_data:
            update_data["message_content"] = template.content

    for field, value in update_data.items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)

    return campaign


async def delete_campaign(
    campaign: Campaign,
    db: AsyncSession,
) -> None:
    if campaign.status != "draft":
        raise ValueError("Only draft campaigns can be deleted")

    await db.delete(campaign)
    await db.commit()


async def submit_campaign(
    campaign: Campaign,
    db: AsyncSession,
) -> Campaign:
    if campaign.status != "draft":
        raise ValueError(
            "Only draft campaigns can be submitted for approval"
        )

    campaign.status = "pending_approval"
    campaign.submitted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(campaign)

    return campaign


async def get_pending_campaigns(
    db: AsyncSession,
) -> list[Campaign]:
    result = await db.execute(
        select(Campaign)
        .where(Campaign.status == "pending_approval")
        .order_by(Campaign.submitted_at.asc())
    )

    return list(result.scalars().all())


async def approve_campaign(
    campaign: Campaign,
    approved_by: int,
    db: AsyncSession,
) -> Campaign:
    if campaign.status != "pending_approval":
        raise ValueError(
            "Only campaigns pending approval can be approved"
        )

    campaign.status = "approved"
    campaign.approved_by = approved_by
    campaign.approved_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(campaign)

    return campaign


async def get_campaign_for_review(
    campaign_id: int,
    db: AsyncSession,
) -> Campaign | None:
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id
        )
    )

    return result.scalar_one_or_none()


async def reject_campaign(
    campaign: Campaign,
    rejected_by: int,
    rejection_reason: str,
    db: AsyncSession,
) -> Campaign:
    if campaign.status != "pending_approval":
        raise ValueError(
            "Only campaigns pending approval can be rejected"
        )

    if not rejection_reason.strip():
        raise ValueError("Rejection reason is required")

    campaign.status = "rejected"
    campaign.rejected_by = rejected_by
    campaign.rejected_at = datetime.now(timezone.utc)
    campaign.rejection_reason = rejection_reason.strip()

    await db.commit()
    await db.refresh(campaign)

    return campaign
