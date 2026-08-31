from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class SendResult:
    def __init__(self, success: bool, provider_message_id: Optional[str] = None, error_message: Optional[str] = None):
        self.success = success
        self.provider_message_id = provider_message_id
        self.error_message = error_message


class BaseMailboxProvider(ABC):
    """
    Abstract Mailbox Provider Interface for legitimate email provider integrations.
    """

    def __init__(self, provider_name: str, is_synthetic: bool = False):
        self.provider_name = provider_name
        self.is_synthetic = is_synthetic

    @abstractmethod
    async def validate_connection(self, mailbox_info: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def get_quota(self, mailbox_info: Dict[str, Any]) -> Dict[str, int]:
        pass

    @abstractmethod
    async def send_message(
        self, mailbox_info: Dict[str, Any], recipient_email: str, subject: str, body: str, preview_text: Optional[str] = None
    ) -> SendResult:
        pass
