from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import JobService
from app.services.orchestrator import JobOrchestrator

router = APIRouter(prefix="/generation-jobs", tags=["Generation Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_generation_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Enqueues a new background lead generation job and triggers the orchestrator.
    """
    job_service = JobService(db)
    job = await job_service.create_job(payload)

    # Launch background job orchestration
    background_tasks.add_task(JobOrchestrator.run_job, job.id)

    return job


@router.get("", response_model=List[JobResponse])
async def list_generation_jobs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    job_service = JobService(db)
    return await job_service.get_jobs(limit=limit)


@router.get("/{job_id}", response_model=JobResponse)
async def get_generation_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    job_service = JobService(db)
    job = await job_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_generation_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    job_service = JobService(db)
    job = await job_service.cancel_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
    return job


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_generation_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    job_service = JobService(db)
    new_job = await job_service.retry_job(job_id)
    if not new_job:
        raise HTTPException(status_code=404, detail="Original job not found")

    background_tasks.add_task(JobOrchestrator.run_job, new_job.id)
    return new_job
