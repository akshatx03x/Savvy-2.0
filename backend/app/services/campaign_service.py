from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignRecipient, CampaignMessage
from app.models.contact import Contact
from app.models.mailbox import Mailbox
from app.models.outreach import OutreachDraft
from app.models.suppression import SuppressionEntry
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignReviewResponse
from app.core.config import settings


class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(self, data: CampaignCreate) -> Campaign:
        campaign = Campaign(
            name=data.name,
            description=data.description,
            status="DRAFT",
            timezone=data.timezone,
            schedule_config=data.schedule_config or {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "start_hour": "09:00",
                "end_hour": "17:00",
                "daily_limit": 150,
                "min_delay_seconds": 60,
            },
            total_recipients=len(data.contact_ids),
            mailbox_ids=data.mailbox_ids,
            is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
        )
        self.db.add(campaign)
        await self.db.flush()

        for contact_id in data.contact_ids:
            rec = CampaignRecipient(
                campaign_id=campaign.id,
                contact_id=contact_id,
                status="PENDING",
            )
            self.db.add(rec)

        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def review_campaign_launch(self, campaign_id: str) -> CampaignReviewResponse:
        stmt = select(Campaign).options(selectinload(Campaign.recipients)).where(Campaign.id == campaign_id)
        res = await self.db.execute(stmt)
        campaign = res.scalars().first()

        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        contact_ids = [r.contact_id for r in campaign.recipients]

        # Check suppression
        stmt_supp = select(SuppressionEntry.contact_id).where(SuppressionEntry.contact_id.in_(contact_ids))
        res_supp = await self.db.execute(stmt_supp)
        suppressed_ids = set(res_supp.scalars().all())

        # Check approved outreach
        stmt_drafts = (
            select(OutreachDraft.contact_id)
            .where(OutreachDraft.contact_id.in_(contact_ids))
            .where(OutreachDraft.status == "APPROVED")
        )
        res_drafts = await self.db.execute(stmt_drafts)
        approved_contact_ids = set(res_drafts.scalars().all())

        # Check mailboxes
        stmt_mb = select(Mailbox).where(Mailbox.id.in_(campaign.mailbox_ids))
        res_mb = await self.db.execute(stmt_mb)
        mailboxes = list(res_mb.scalars().all())
        total_capacity = sum([m.daily_send_limit - m.current_usage for m in mailboxes if m.connection_status == "CONNECTED"])

        warnings = []
        approved_count = len(approved_contact_ids)
        missing_count = len(contact_ids) - approved_count
        suppressed_count = len(suppressed_ids)

        if missing_count > 0:
            warnings.append(f"⚠ {missing_count} contacts do not have approved Module 3 outreach drafts.")

        if suppressed_count > 0:
            warnings.append(f"⚠ {suppressed_count} recipients are on the suppression list and will be excluded.")

        if total_capacity < len(contact_ids):
            warnings.append(f"⚠ Daily mailbox capacity ({total_capacity}) is lower than target recipients ({len(contact_ids)}). Queueing will apply.")

        can_launch = len(mailboxes) > 0 and (approved_count > 0)

        return CampaignReviewResponse(
            campaign_name=campaign.name,
            total_recipients=len(contact_ids),
            approved_messages_count=approved_count,
            missing_outreach_count=missing_count,
            suppressed_count=suppressed_count,
            invalid_count=0,
            selected_mailboxes_count=len(mailboxes),
            total_daily_capacity=total_capacity,
            warnings=warnings,
            can_launch=can_launch,
        )

    async def launch_campaign(self, campaign_id: str) -> Campaign:
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")

        review = await self.review_campaign_launch(campaign_id)
        if not review.can_launch:
            raise ValueError("Campaign cannot be launched. Please assign connected mailboxes and approved outreach.")

        campaign.status = "ACTIVE"
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def pause_campaign(self, campaign_id: str) -> Campaign:
        campaign = await self.get_campaign_by_id(campaign_id)
        if campaign:
            campaign.status = "PAUSED"
            await self.db.commit()
            await self.db.refresh(campaign)
        return campaign

    async def resume_campaign(self, campaign_id: str) -> Campaign:
        campaign = await self.get_campaign_by_id(campaign_id)
        if campaign:
            campaign.status = "ACTIVE"
            await self.db.commit()
            await self.db.refresh(campaign)
        return campaign

    async def get_campaigns(self) -> List[Campaign]:
        stmt = select(Campaign).order_by(desc(Campaign.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Campaign]:
        stmt = select(Campaign).options(selectinload(Campaign.recipients)).where(Campaign.id == campaign_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()
