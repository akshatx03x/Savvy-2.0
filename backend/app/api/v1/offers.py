from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.offer import OfferCreate, OfferUpdate, OfferResponse
from app.services.offer_service import OfferService

router = APIRouter(prefix="/offers", tags=["Offer Profiles"])


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(payload: OfferCreate, db: AsyncSession = Depends(get_db)):
    service = OfferService(db)
    return await service.create_offer(payload)


@router.get("", response_model=List[OfferResponse])
async def list_offers(active_only: bool = False, db: AsyncSession = Depends(get_db)):
    service = OfferService(db)
    return await service.get_offers(active_only=active_only)


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(offer_id: str, db: AsyncSession = Depends(get_db)):
    service = OfferService(db)
    offer = await service.get_offer_by_id(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer profile not found")
    return offer


@router.patch("/{offer_id}", response_model=OfferResponse)
async def update_offer(offer_id: str, payload: OfferUpdate, db: AsyncSession = Depends(get_db)):
    service = OfferService(db)
    offer = await service.update_offer(offer_id, payload)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer profile not found")
    return offer


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(offer_id: str, db: AsyncSession = Depends(get_db)):
    service = OfferService(db)
    deleted = await service.delete_offer(offer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Offer profile not found")
    return None
