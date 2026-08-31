from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics import DeliverabilityOverviewResponse
from app.services.deliverability_service import DeliverabilityService

router = APIRouter(prefix="/deliverability", tags=["Deliverability Center"])


@router.get("/overview", response_model=DeliverabilityOverviewResponse)
async def get_deliverability_overview(db: AsyncSession = Depends(get_db)):
    service = DeliverabilityService(db)
    return await service.get_overview()
