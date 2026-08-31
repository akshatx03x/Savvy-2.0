from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.outreach import (
    OutreachGenerationRequest,
    OutreachRewriteRequest,
    OutreachDraftResponse,
    OutreachJobCreate,
    OutreachJobResponse,
    Module4OutreachContract,
)
from app.services.outreach_service import OutreachService
from app.services.outreach_orchestrator import OutreachOrchestrator

router = APIRouter(prefix="/outreach", tags=["AI Personalization & Outreach Studio"])


@router.post("/generate", response_model=OutreachDraftResponse, status_code=status.HTTP_201_CREATED)
async def generate_outreach_draft(
    payload: OutreachGenerationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generates single-lead personalized outreach draft.
    """
    service = OutreachService(db)
    try:
        return await service.generate_outreach_draft(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-bulk", response_model=OutreachJobResponse, status_code=status.HTTP_201_CREATED)
async def generate_bulk_outreach(
    payload: OutreachJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Enqueues bulk outreach generation job.
    """
    service = OutreachService(db)
    job = await service.create_outreach_job(payload)
    background_tasks.add_task(OutreachOrchestrator.run_job, job.id)
    return job


@router.get("/drafts", response_model=List[OutreachDraftResponse])
async def list_outreach_drafts(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    return await service.get_drafts(status=status, limit=limit)


@router.get("/drafts/{draft_id}", response_model=OutreachDraftResponse)
async def get_outreach_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    draft = await service.get_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Outreach draft not found")
    return draft


@router.patch("/drafts/{draft_id}", response_model=OutreachDraftResponse)
async def update_outreach_draft(
    draft_id: str,
    updates: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    try:
        return await service.update_draft(draft_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/drafts/{draft_id}/approve", response_model=OutreachDraftResponse)
async def approve_outreach_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    try:
        return await service.approve_draft(draft_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/drafts/{draft_id}/archive", response_model=OutreachDraftResponse)
async def archive_outreach_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    try:
        return await service.archive_draft(draft_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/drafts/{draft_id}/rewrite", response_model=OutreachDraftResponse)
async def rewrite_outreach_draft(
    draft_id: str,
    payload: OutreachRewriteRequest,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    try:
        return await service.rewrite_draft(draft_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=List[OutreachJobResponse])
async def list_outreach_jobs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    return await service.get_outreach_jobs(limit=limit)


@router.get("/jobs/{job_id}", response_model=OutreachJobResponse)
async def get_outreach_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = OutreachService(db)
    job = await service.get_outreach_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Outreach job not found")
    return job


@router.get("/module4-contract/{draft_id}", response_model=Module4OutreachContract)
async def get_module4_outreach_contract(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    MODULE 4 CONTRACT ENDPOINT:
    Returns approved outreach message payload ready for sending in Module 4.
    """
    service = OutreachService(db)
    try:
        return await service.get_module4_contract(draft_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
