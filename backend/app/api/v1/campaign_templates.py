from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.campaign_template import (
    CampaignTemplateCreate,
    CampaignTemplateUpdate,
    CampaignTemplateResponse,
)
from app.services.campaign_template_service import (
    create_template,
    get_all_templates,
    get_template_by_id,
    update_template,
    delete_template,
)


router = APIRouter(
    prefix="/campaign-templates",
    tags=["Campaign Templates"],
)


@router.post(
    "/",
    response_model=CampaignTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign_template(
    template_data: CampaignTemplateCreate,
    current_user: User = Depends(require_permission("templates.create")),
    db: AsyncSession = Depends(get_db),
):
    return await create_template(
        template_data,
        current_user.id,
        db,
    )


@router.get(
    "/",
    response_model=list[CampaignTemplateResponse],
)
async def list_campaign_templates(
    current_user: User = Depends(require_permission("templates.read")),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_templates(db)


@router.get(
    "/{template_id}",
    response_model=CampaignTemplateResponse,
)
async def get_campaign_template(
    template_id: int,
    current_user: User = Depends(require_permission("templates.read")),
    db: AsyncSession = Depends(get_db),
):
    template = await get_template_by_id(template_id, db)

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign template not found",
        )

    return template


@router.patch(
    "/{template_id}",
    response_model=CampaignTemplateResponse,
)
async def update_campaign_template(
    template_id: int,
    template_data: CampaignTemplateUpdate,
    current_user: User = Depends(require_permission("templates.update")),
    db: AsyncSession = Depends(get_db),
):
    template = await get_template_by_id(template_id, db)

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign template not found",
        )

    return await update_template(
        template,
        template_data,
        db,
    )


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_campaign_template(
    template_id: int,
    current_user: User = Depends(require_permission("templates.delete")),
    db: AsyncSession = Depends(get_db),
):
    template = await get_template_by_id(template_id, db)

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign template not found",
        )

    await delete_template(template, db)

    return Response(status_code=status.HTTP_204_NO_CONTENT)