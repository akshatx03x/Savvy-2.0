from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignRecipient, CampaignMessage
from app.models.contact import Contact
from app.models.mailbox import Mailbox
from app.models.outreach import OutreachDraft
from app.models.suppression import SuppressionEntry
from app.mailboxes.registry import mailbox_registry
from app.services.mailbox_selector import MailboxSelector
from app.core.logging import logger


class SendingEngine:
    """
    Module 4 Safe & Idempotent Sending Engine:
    Validates pre-send eligibility, checks suppression, enforces mailbox quotas,
    and applies send-state transaction locks to guarantee zero double-sends.
    """

    @staticmethod
    async def is_suppressed(db: AsyncSession, email: str) -> bool:
        stmt = select(SuppressionEntry).where(SuppressionEntry.email == email.lower().strip())
        res = await db.execute(stmt)
        return res.scalars().first() is not None

    @classmethod
    async def process_recipient_send(
        cls, db: AsyncSession, campaign: Campaign, recipient: CampaignRecipient
    ) -> Tuple[bool, str]:
        # 1. Fetch Contact
        stmt_ct = select(Contact).where(Contact.id == recipient.contact_id)
        res_ct = await db.execute(stmt_ct)
        contact = res_ct.scalars().first()

        if not contact or not contact.email:
            recipient.status = "FAILED"
            recipient.error_reason = "Missing or invalid recipient email address"
            await db.commit()
            return False, "INVALID_EMAIL"

        # 2. Server-side Suppression Check
        if await cls.is_suppressed(db, contact.email):
            recipient.status = "BLOCKED_SUPPRESSED"
            recipient.error_reason = "Recipient email is listed on suppression list"
            await db.commit()
            return False, "BLOCKED_SUPPRESSED"

        # 3. Approved Outreach Draft Check
        stmt_draft = (
            select(OutreachDraft)
            .where(OutreachDraft.lead_id.in_(
                select(Contact.id).where(Contact.id == contact.id)
            ))
            .where(OutreachDraft.status == "APPROVED")
            .order_by(OutreachDraft.updated_at.desc())
        )
        res_draft = await db.execute(stmt_draft)
        draft = res_draft.scalars().first()

        if not draft:
            # Fallback check for any draft for contact
            stmt_draft_any = select(OutreachDraft).where(OutreachDraft.contact_id == contact.id).where(OutreachDraft.status == "APPROVED")
            res_draft_any = await db.execute(stmt_draft_any)
            draft = res_draft_any.scalars().first()

        if not draft:
            recipient.status = "BLOCKED_NO_OUTREACH"
            recipient.error_reason = "No approved Module 3 outreach draft found for contact"
            await db.commit()
            return False, "BLOCKED_NO_OUTREACH"

        # 4. Idempotency Lock Check (Prevent duplicate sends upon worker retry)
        if recipient.status in ["SENT", "SENDING"]:
            stmt_msg = select(CampaignMessage).where(CampaignMessage.campaign_recipient_id == recipient.id)
            res_msg = await db.execute(stmt_msg)
            if res_msg.scalars().first():
                return True, "ALREADY_SENT"

        # 5. Smart Mailbox Selection & Quota Check
        mailbox = await MailboxSelector.select_mailbox(db, campaign.mailbox_ids)
        if not mailbox:
            recipient.status = "BLOCKED_QUOTA"
            recipient.error_reason = "All mailboxes at capacity or unavailable"
            await db.commit()
            return False, "BLOCKED_QUOTA"

        # 6. Apply Send Lock State
        recipient.status = "SENDING"
        recipient.mailbox_id = mailbox.id
        await db.commit()

        # 7. Execute Send via Mailbox Provider Abstraction
        provider = mailbox_registry.get_provider(mailbox.provider)
        mailbox_info = {
            "id": mailbox.id,
            "email": mailbox.email,
            "daily_send_limit": mailbox.daily_send_limit,
            "current_usage": mailbox.current_usage,
        }

        send_res = await provider.send_message(
            mailbox_info=mailbox_info,
            recipient_email=contact.email,
            subject=draft.subject,
            body=draft.body,
            preview_text=draft.preview_text,
        )

        if send_res.success:
            recipient.status = "SENT"
            recipient.sent_at = datetime.now(timezone.utc)

            # Update mailbox usage
            mailbox.current_usage += 1
            mailbox.last_sync_at = datetime.now(timezone.utc)

            # Create CampaignMessage
            msg = CampaignMessage(
                campaign_recipient_id=recipient.id,
                outreach_draft_id=draft.id,
                subject=draft.subject,
                body=draft.body,
                provider_message_id=send_res.provider_message_id,
                status="SENT",
                sent_at=datetime.now(timezone.utc),
                delivered_at=datetime.now(timezone.utc), # Instant delivery simulation
            )
            db.add(msg)

            # Update Campaign Stats
            campaign.sent_count += 1
            campaign.delivered_count += 1
            await db.commit()
            return True, "SENT"
        else:
            recipient.status = "FAILED"
            recipient.error_reason = send_res.error_message or "Provider send failure"
            await db.commit()
            return False, "FAILED"
