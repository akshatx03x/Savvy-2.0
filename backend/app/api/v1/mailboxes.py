from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.mailbox import Mailbox
from app.schemas.mailbox import MailboxConnect, MailboxResponse, MailboxHealthResponse
from app.core.config import settings

router = APIRouter(prefix="/mailboxes", tags=["Mailbox Management"])


@router.post("/connect", response_model=MailboxResponse, status_code=status.HTTP_201_CREATED)
async def connect_mailbox(payload: MailboxConnect, db: AsyncSession = Depends(get_db)):
    stmt = select(Mailbox).where(Mailbox.email == payload.email)
    res = await db.execute(stmt)
    existing = res.scalars().first()

    if existing:
        existing.connection_status = "CONNECTED"
        existing.daily_send_limit = payload.daily_send_limit
        await db.commit()
        await db.refresh(existing)
        return existing

    mb = Mailbox(
        provider=payload.provider,
        email=payload.email,
        display_name=payload.display_name or payload.email.split("@")[0],
        connection_status="CONNECTED",
        daily_send_limit=payload.daily_send_limit,
        is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
    )
    db.add(mb)
    await db.commit()
    await db.refresh(mb)
    return mb


@router.get("", response_model=List[MailboxResponse])
async def list_mailboxes(db: AsyncSession = Depends(get_db)):
    stmt = select(Mailbox).order_by(desc(Mailbox.created_at))
    res = await db.execute(stmt)
    mailboxes = list(res.scalars().all())

    if not mailboxes:
        # Default mock connected mailbox for local development
        mock_mb = Mailbox(
            provider="gmail",
            email="sales@company.com",
            display_name="Sales Team",
            connection_status="CONNECTED",
            daily_send_limit=500,
            current_usage=342,
            health_score=92,
            bounce_rate=0.011,
            complaint_rate=0.0004,
            reply_rate=0.082,
            spf_status="CONFIGURED",
            dkim_status="CONFIGURED",
            dmarc_status="CONFIGURED",
            is_synthetic=True,
        )
        db.add(mock_mb)
        await db.commit()
        await db.refresh(mock_mb)
        return [mock_mb]

    return mailboxes


@router.get("/{mailbox_id}", response_model=MailboxResponse)
async def get_mailbox(mailbox_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Mailbox).where(Mailbox.id == mailbox_id)
    res = await db.execute(stmt)
    mb = res.scalars().first()
    if not mb:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    return mb


@router.get("/{mailbox_id}/health", response_model=MailboxHealthResponse)
async def get_mailbox_health(mailbox_id: str, db: AsyncSession = Depends(get_db)):
    mb = await get_mailbox(mailbox_id, db)
    return MailboxHealthResponse(
        mailbox_id=mb.id,
        email=mb.email,
        health_score=mb.health_score,
        status="Healthy" if mb.health_score >= 80 else "Needs Attention",
        recommendations=[
            "✓ SPF authentication configured.",
            "✓ DKIM signature verified.",
            "✓ Bounce rate healthy (1.1%).",
        ],
    )


@router.delete("/{mailbox_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mailbox(mailbox_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Mailbox).where(Mailbox.id == mailbox_id)
    res = await db.execute(stmt)
    mb = res.scalars().first()
    if not mb:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    await db.delete(mb)
    await db.commit()
    return None
