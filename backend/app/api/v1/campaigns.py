from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignReviewResponse,
)
from app.services.campaign_service import CampaignService
from app.services.campaign_orchestrator import CampaignOrchestrator

router = APIRouter(prefix="/campaigns", tags=["Outreach Campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(payload: CampaignCreate, db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    return await service.create_campaign(payload)


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    campaigns = await service.get_campaigns()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    c = await service.get_campaign_by_id(campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c


@router.get("/{campaign_id}/review", response_model=CampaignReviewResponse)
async def review_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    try:
        return await service.review_campaign_launch(campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/launch", response_model=CampaignResponse)
async def launch_campaign(
    campaign_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    service = CampaignService(db)
    try:
        c = await service.launch_campaign(campaign_id)
        background_tasks.add_task(CampaignOrchestrator.run_campaign_batch, c.id)
        return c
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    return await service.pause_campaign(campaign_id)


@router.post("/{campaign_id}/resume", response_model=CampaignResponse)
async def resume_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    return await service.resume_campaign(campaign_id)
