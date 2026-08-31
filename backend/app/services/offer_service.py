from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.offer import OfferProfile
from app.schemas.offer import OfferCreate, OfferUpdate
from app.core.config import settings


class OfferService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_offer(self, data: OfferCreate) -> OfferProfile:
        offer = OfferProfile(
            name=data.name,
            description=data.description,
            target_customer=data.target_customer,
            value_proposition=data.value_proposition,
            differentiators=data.differentiators,
            proof_points=data.proof_points,
            cta=data.cta,
            tone_preferences=data.tone_preferences,
            is_active=data.is_active,
            is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
        )
        self.db.add(offer)
        await self.db.commit()
        await self.db.refresh(offer)
        return offer

    async def get_offers(self, active_only: bool = True) -> List[OfferProfile]:
        stmt = select(OfferProfile)
        if active_only:
            stmt = stmt.where(OfferProfile.is_active == True)
        stmt = stmt.order_by(desc(OfferProfile.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_offer_by_id(self, offer_id: str) -> Optional[OfferProfile]:
        stmt = select(OfferProfile).where(OfferProfile.id == offer_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def update_offer(self, offer_id: str, data: OfferUpdate) -> Optional[OfferProfile]:
        offer = await self.get_offer_by_id(offer_id)
        if not offer:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(offer, key, val)

        await self.db.commit()
        await self.db.refresh(offer)
        return offer

    async def delete_offer(self, offer_id: str) -> bool:
        offer = await self.get_offer_by_id(offer_id)
        if not offer:
            return False
        await self.db.delete(offer)
        await self.db.commit()
        return True
