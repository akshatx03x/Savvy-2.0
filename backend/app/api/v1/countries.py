from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.stats import CountryStat
from app.services.lead_service import LeadService

router = APIRouter(prefix="/countries", tags=["Country Organization"])


@router.get("", response_model=List[CountryStat])
async def list_country_stats(db: AsyncSession = Depends(get_db)):
    """
    STRICT GEOGRAPHIC RULE:
    Country is the ONLY geographic categorization level.
    Returns aggregated stats per Country.
    """
    service = LeadService(db)
    return await service.get_country_stats()
