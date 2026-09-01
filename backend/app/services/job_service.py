from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import GenerationJob, JobLog
from app.schemas.job import JobCreate
from app.schemas.ai import SearchPlanResponse
from app.core.config import settings


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, data: JobCreate) -> GenerationJob:
        plan: SearchPlanResponse = data.plan
        job_name = data.name or f"{plan.niche} Leads in {plan.country}"

        job = GenerationJob(
            name=job_name,
            search_type=data.search_type,
            status="QUEUED",
            query_params=plan.model_dump(),
            niche=plan.niche,
            country=plan.country,
            requested_count=plan.quantity,
            progress_percentage=0,
            is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        self.db.add(JobLog(job_id=job.id, level="INFO", message="Job queued for execution", step="QUEUED"))
        await self.db.commit()

        return await self.get_job_by_id(job.id)

    async def get_jobs(self, limit: int = 50) -> List[GenerationJob]:
        stmt = select(GenerationJob).options(selectinload(GenerationJob.logs)).order_by(desc(GenerationJob.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_job_by_id(self, job_id: str) -> Optional[GenerationJob]:
        stmt = select(GenerationJob).options(selectinload(GenerationJob.logs)).where(GenerationJob.id == job_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def cancel_job(self, job_id: str) -> Optional[GenerationJob]:
        job = await self.get_job_by_id(job_id)
        if job and job.status in ["QUEUED", "PLANNING", "SEARCHING", "PROCESSING"]:
            job.status = "CANCELLED"
            job.completed_at = datetime.now(timezone.utc)
            self.db.add(JobLog(job_id=job.id, level="WARNING", message="User requested job cancellation", step="CANCELLED"))
            await self.db.commit()
            await self.db.refresh(job)
        return job

    async def retry_job(self, job_id: str) -> Optional[GenerationJob]:
        existing = await self.get_job_by_id(job_id)
        if not existing:
            return None

        plan = SearchPlanResponse(**existing.query_params)
        new_job = await self.create_job(JobCreate(name=f"Retry: {existing.name}", search_type=existing.search_type, plan=plan))
        return new_job
