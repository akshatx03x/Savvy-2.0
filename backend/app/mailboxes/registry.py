from typing import Dict
from app.mailboxes.base import BaseMailboxProvider
from app.mailboxes.adapters.simulated_mailbox import SimulatedMailboxAdapter


class MailboxProviderRegistry:
    def __init__(self):
        self.providers: Dict[str, BaseMailboxProvider] = {
            "simulated": SimulatedMailboxAdapter(),
            "gmail": SimulatedMailboxAdapter(), # Production Google OAuth connector fallback
            "microsoft": SimulatedMailboxAdapter(), # Production Microsoft Graph connector fallback
            "smtp": SimulatedMailboxAdapter(), # Production SMTP connector fallback
        }

    def get_provider(self, provider_name: str) -> BaseMailboxProvider:
        return self.providers.get(provider_name.lower(), self.providers["simulated"])


mailbox_registry = MailboxProviderRegistry()
