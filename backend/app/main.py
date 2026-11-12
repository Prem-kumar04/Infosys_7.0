from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.audiences import router as audiences_router
from app.api.v1.audience_segments import router as audience_segments_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.campaign_templates import router as campaign_templates_router


app = FastAPI(
    title="Infosys 7.0 API",
    description="Backend API for BhashaConnect AI campaign and audience management",
    version="1.0.0",
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(audiences_router, prefix="/api/v1")
app.include_router(audience_segments_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(campaign_templates_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Infosys 7.0 API",
        "status": "success",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}