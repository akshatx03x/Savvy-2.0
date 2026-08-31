from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.suppression import SuppressionEntry
from app.schemas.suppression import SuppressionCreate, SuppressionResponse

router = APIRouter(prefix="/suppression", tags=["Suppression List"])


@router.get("", response_model=List[SuppressionResponse])
async def list_suppressed(db: AsyncSession = Depends(get_db)):
    stmt = select(SuppressionEntry).order_by(desc(SuppressionEntry.created_at))
    res = await db.execute(stmt)
    entries = list(res.scalars().all())

    if not entries:
        mock_entry = SuppressionEntry(
            email="optout@example.com",
            reason="OPT_OUT",
            source="user_optout_link",
        )
        db.add(mock_entry)
        await db.commit()
        await db.refresh(mock_entry)
        return [mock_entry]

    return entries


@router.post("", response_model=SuppressionResponse, status_code=status.HTTP_201_CREATED)
async def add_suppressed(payload: SuppressionCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(SuppressionEntry).where(SuppressionEntry.email == payload.email)
    res = await db.execute(stmt)
    existing = res.scalars().first()
    if existing:
        return existing

    entry = SuppressionEntry(
        email=payload.email.lower().strip(),
        contact_id=payload.contact_id,
        reason=payload.reason,
        source=payload.source,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_suppressed(entry_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(SuppressionEntry).where(SuppressionEntry.id == entry_id)
    res = await db.execute(stmt)
    entry = res.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="Suppression entry not found")
    await db.delete(entry)
    await db.commit()
    return None
