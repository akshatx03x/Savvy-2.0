from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics import GlobalAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Unified SaaS Analytics"])


@router.get("/overview", response_model=GlobalAnalyticsResponse)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_global_overview()
