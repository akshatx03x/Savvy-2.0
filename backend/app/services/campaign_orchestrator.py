import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignRecipient
from app.services.sending_engine import SendingEngine
from app.core.database import AsyncSessionLocal
from app.core.logging import logger


class CampaignOrchestrator:
    """
    Asynchronous Background Campaign Processing Engine.
    Executes sends while enforcing quotas, safety thresholds, and schedule windows.
    """

    @staticmethod
    async def run_campaign_batch(campaign_id: str):
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(Campaign).options(selectinload(Campaign.recipients)).where(Campaign.id == campaign_id)
                res = await db.execute(stmt)
                campaign: Optional[Campaign] = res.scalars().first()

                if not campaign or campaign.status != "ACTIVE":
                    return

                pending_recipients = [r for r in campaign.recipients if r.status == "PENDING"]

                for recipient in pending_recipients:
                    # Check campaign status cancellation/pause
                    stmt_chk = select(Campaign.status).where(Campaign.id == campaign_id)
                    chk_res = await db.execute(stmt_chk)
                    if chk_res.scalar() != "ACTIVE":
                        break

                    success, status_code = await SendingEngine.process_recipient_send(db, campaign, recipient)
                    await asyncio.sleep(0.1) # Controlled delay

                # Check if all completed
                stmt_rec_all = select(CampaignRecipient).where(CampaignRecipient.campaign_id == campaign_id)
                res_all = await db.execute(stmt_rec_all)
                all_recipients = list(res_all.scalars().all())

                if all(r.status in ["SENT", "FAILED", "BLOCKED_SUPPRESSED", "BLOCKED_NO_OUTREACH"] for r in all_recipients):
                    campaign.status = "COMPLETED"
                    await db.commit()

            except Exception as e:
                logger.error(f"Error processing campaign {campaign_id}: {e}", exc_info=True)
