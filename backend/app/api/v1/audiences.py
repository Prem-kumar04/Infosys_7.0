
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.audience import (
    AudienceCreate,
    AudienceResponse,
    AudienceUpdate,
)
from app.services.audience_service import (
    create_audience,
    delete_audience,
    filter_audiences,
    get_all_audiences,
    get_audience_by_id,
    update_audience,
)
from app.services.audience_import_service import (
    import_audiences_from_csv,
)

router = APIRouter(
    prefix="/audiences",
    tags=["Audience Management"],
)


@router.post(
    "/",
    response_model=AudienceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audience_endpoint(
    audience_data: AudienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.create")),
):
    try:
        return await create_audience(audience_data, db)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or phone number already exists",
        )


@router.get("/", response_model=list[AudienceResponse])
async def list_audiences_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.read")),
):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values",
        )

    return await get_all_audiences(db, skip, limit)


# Keep this route before /{audience_id}.
@router.get("/filter", response_model=list[AudienceResponse])
async def filter_audiences_endpoint(
    gender: str | None = None,
    preferred_language: str | None = None,
    state: str | None = None,
    city: str | None = None,
    occupation: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.read")),
):
    return await filter_audiences(
        db=db,
        gender=gender,
        preferred_language=preferred_language,
        state=state,
        city=city,
        occupation=occupation,
    )


@router.post("/import")
async def import_audiences_endpoint(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.create")),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed",
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV file is empty",
        )

    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="CSV file must not exceed 5 MB",
        )

    try:
        return await import_audiences_from_csv(file_content, db)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="CSV import failed due to a server error",
        )


@router.get("/{audience_id}", response_model=AudienceResponse)
async def get_audience_endpoint(
    audience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.read")),
):
    audience = await get_audience_by_id(audience_id, db)

    if audience is None:
        raise HTTPException(
            status_code=404,
            detail="Audience record not found",
        )

    return audience


@router.patch("/{audience_id}", response_model=AudienceResponse)
async def update_audience_endpoint(
    audience_id: int,
    audience_data: AudienceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.update")),
):
    audience = await get_audience_by_id(audience_id, db)

    if audience is None:
        raise HTTPException(
            status_code=404,
            detail="Audience record not found",
        )

    try:
        return await update_audience(audience, audience_data, db)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or phone number already exists",
        )
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )


@router.delete(
    "/{audience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_audience_endpoint(
    audience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("audience.delete")),
):
    audience = await get_audience_by_id(audience_id, db)

    if audience is None:
        raise HTTPException(
            status_code=404,
            detail="Audience record not found",
        )

    await delete_audience(audience, db)
    return None
