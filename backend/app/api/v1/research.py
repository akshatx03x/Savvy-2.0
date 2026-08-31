from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.research import (
    ResearchJobCreate,
    ResearchJobResponse,
    ResearchProfileResponse,
    Module3ResearchContract,
)
from app.services.research_service import ResearchService
from app.services.research_orchestrator import ResearchOrchestrator

router = APIRouter(prefix="/research", tags=["AI Web Research & Lead Intelligence"])


@router.post("/jobs", response_model=ResearchJobResponse, status_code=status.HTTP_201_CREATED)
async def create_research_job(
    payload: ResearchJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Enqueues a bulk or single-lead research job.
    """
    service = ResearchService(db)
    job = await service.create_research_job(payload)

    # Trigger background research orchestrator
    background_tasks.add_task(ResearchOrchestrator.run_job, job.id)
    return job


@router.get("/jobs", response_model=List[ResearchJobResponse])
async def list_research_jobs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    service = ResearchService(db)
    return await service.get_research_jobs(limit=limit)


@router.get("/jobs/{job_id}", response_model=ResearchJobResponse)
async def get_research_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ResearchService(db)
    job = await service.get_research_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    return job


@router.post("/jobs/{job_id}/cancel", response_model=ResearchJobResponse)
async def cancel_research_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ResearchService(db)
    job = await service.cancel_research_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found or cannot be cancelled")
    return job


@router.get("/leads/{lead_id}", response_model=ResearchProfileResponse)
async def get_lead_research_profile(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns full AI Intelligence Profile for a specific lead.
    """
    service = ResearchService(db)
    profile = await service.get_profile_by_lead_id(lead_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Research profile not found for this lead")
    return profile


@router.post("/leads/{lead_id}/refresh", response_model=ResearchJobResponse)
async def refresh_lead_research(
    lead_id: str,
    depth: str = "standard",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers re-research for a lead.
    """
    service = ResearchService(db)
    job = await service.create_research_job(
        ResearchJobCreate(lead_ids=[lead_id], research_depth=depth, name=f"Refresh Research (Lead {lead_id[:8]})")
    )
    background_tasks.add_task(ResearchOrchestrator.run_job, job.id)
    return job


@router.get("/leads/{lead_id}/contract", response_model=Module3ResearchContract)
async def get_module3_research_contract(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    MODULE 3 CONTRACT ENDPOINT:
    Returns structured intelligence payload consumed by Module 3.
    """
    service = ResearchService(db)
    try:
        return await service.get_module3_contract(lead_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
