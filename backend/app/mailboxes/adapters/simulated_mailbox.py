import uuid
from typing import Dict, Any, Optional
from app.mailboxes.base import BaseMailboxProvider, SendResult
from app.core.config import settings


class SimulatedMailboxAdapter(BaseMailboxProvider):
    """
    Simulated Mailbox Provider Adapter for local development & automated testing.
    """

    def __init__(self):
        super().__init__(provider_name="simulated", is_synthetic=True)

    async def validate_connection(self, mailbox_info: Dict[str, Any]) -> bool:
        return True

    async def get_quota(self, mailbox_info: Dict[str, Any]) -> Dict[str, int]:
        return {
            "daily_limit": mailbox_info.get("daily_send_limit", 500),
            "current_usage": mailbox_info.get("current_usage", 0),
            "remaining": max(0, mailbox_info.get("daily_send_limit", 500) - mailbox_info.get("current_usage", 0)),
        }

    async def send_message(
        self, mailbox_info: Dict[str, Any], recipient_email: str, subject: str, body: str, preview_text: Optional[str] = None
    ) -> SendResult:
        if not settings.ENABLE_SYNTHETIC_DATA and settings.ENVIRONMENT == "production":
            return SendResult(success=False, error_message="Synthetic sending disabled in production mode")


        msg_id = f"sim_msg_{uuid.uuid4().hex[:12]}"
        return SendResult(success=True, provider_message_id=msg_id)
