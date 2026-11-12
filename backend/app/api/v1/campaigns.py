
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignRejectRequest,
    CampaignResponse,
    CampaignUpdate,
)
from app.services.campaign_service import (
    approve_campaign,
    create_campaign,
    delete_campaign,
    get_campaign_by_id,
    get_campaign_for_review,
    get_my_campaigns,
    get_pending_campaigns,
    reject_campaign,
    submit_campaign,
    update_campaign,
)

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaign Management"],
)


@router.post(
    "/",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign_endpoint(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.create")),
):
    try:
        return await create_campaign(
            campaign_data=campaign_data,
            user_id=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/",
    response_model=list[CampaignResponse],
)
async def list_campaigns_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.read")),
):
    return await get_my_campaigns(
        user_id=current_user.id,
        db=db,
    )


@router.get(
    "/pending-review",
    response_model=list[CampaignResponse],
)
async def get_pending_campaigns_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.approve")),
):
    return await get_pending_campaigns(db)


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
async def get_campaign_endpoint(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.read")),
):
    campaign = await get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=current_user.id,
        db=db,
    )

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@router.patch(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
async def update_campaign_endpoint(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.update")),
):
    campaign = await get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=current_user.id,
        db=db,
    )

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        return await update_campaign(
            campaign=campaign,
            campaign_data=campaign_data,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_campaign_endpoint(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.delete")),
):
    campaign = await get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=current_user.id,
        db=db,
    )

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        await delete_campaign(campaign, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return None


@router.post(
    "/{campaign_id}/submit",
    response_model=CampaignResponse,
)
async def submit_campaign_for_approval(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.submit")),
):
    campaign = await get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=current_user.id,
        db=db,
    )

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        return await submit_campaign(campaign=campaign, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{campaign_id}/approve",
    response_model=CampaignResponse,
)
async def approve_campaign_endpoint(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.approve")),
):
    campaign = await get_campaign_for_review(
        campaign_id=campaign_id,
        db=db,
    )

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        return await approve_campaign(
            campaign=campaign,
            approved_by=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{campaign_id}/reject",
    response_model=CampaignResponse,
)
async def reject_campaign_endpoint(
    campaign_id: int,
    rejection_data: CampaignRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("campaigns.reject")),
):
    campaign = await get_campaign_for_review(
        campaign_id=campaign_id,
        db=db,
    )

    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        return await reject_campaign(
            campaign=campaign,
            rejected_by=current_user.id,
            rejection_reason=rejection_data.rejection_reason,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
