from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadResponse, LeadFilter, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("")
async def list_leads(
    search: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    city: Optional[str] = None,
    industry: Optional[str] = None,
    min_score: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    has_email: Optional[bool] = None,
    has_phone: Optional[bool] = None,
    has_website: Optional[bool] = None,
    source: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    filters = LeadFilter(
        search=search,
        country=country,
        region=region,
        city=city,
        industry=industry,
        min_score=min_score,
        status=status_filter,
        has_email=has_email,
        has_phone=has_phone,
        has_website=has_website,
        source=source,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = LeadService(db)
    leads, total = await service.get_leads(filters)

    items = [LeadResponse.model_validate(l).model_dump() for l in leads]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
    }


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if payload.status:
        lead.status = payload.status
    if payload.notes is not None:
        lead.notes = payload.notes
    if payload.lead_score is not None:
        lead.lead_score = payload.lead_score

    db.add(lead)
    await db.commit()
    return await service.get_lead_by_id(lead_id)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Lead).where(Lead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.delete(lead)
    await db.commit()
