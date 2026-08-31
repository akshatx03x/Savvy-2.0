from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mailbox import Mailbox


class MailboxSelector:
    """
    Smart Mailbox Selector Algorithm:
    Selects healthy connected mailboxes with available daily quota capacity.
    """

    @staticmethod
    async def select_mailbox(db: AsyncSession, preferred_mailbox_ids: Optional[List[str]] = None) -> Optional[Mailbox]:
        stmt = select(Mailbox).where(Mailbox.connection_status == "CONNECTED")

        if preferred_mailbox_ids and len(preferred_mailbox_ids) > 0:
            stmt = stmt.where(Mailbox.id.in_(preferred_mailbox_ids))

        res = await db.execute(stmt)
        mailboxes = list(res.scalars().all())

        eligible = [
            m for m in mailboxes
            if m.health_score >= 60 and m.current_usage < m.daily_send_limit
        ]

        if not eligible:
            return None

        # Sort by available capacity & health score
        eligible.sort(key=lambda m: (m.daily_send_limit - m.current_usage, m.health_score), reverse=True)
        return eligible[0]
