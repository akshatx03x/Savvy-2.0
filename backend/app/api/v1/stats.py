from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.stats import DashboardStatsResponse
from app.services.lead_service import LeadService
from app.services.job_service import JobService
from app.schemas.job import JobResponse

router = APIRouter(prefix="/stats", tags=["Dashboard Analytics"])


@router.get("", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    lead_service = LeadService(db)
    job_service = JobService(db)

    stats = await lead_service.get_dashboard_stats()
    recent_jobs = await job_service.get_jobs(limit=5)
    
    stats.generation_jobs_count = len(recent_jobs)
    stats.recent_jobs = [JobResponse.model_validate(j).model_dump() for j in recent_jobs]

    return stats
