from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class MailboxConnect(BaseModel):
    provider: str = Field("gmail", description="gmail, microsoft, smtp, simulated")
    email: str
    display_name: Optional[str] = None
    daily_send_limit: int = 500


class MailboxResponse(BaseModel):
    id: str
    provider: str
    email: str
    display_name: Optional[str] = None
    connection_status: str
    daily_send_limit: int
    current_usage: int
    health_score: int
    bounce_rate: float
    complaint_rate: float
    reply_rate: float
    spf_status: str
    dkim_status: str
    dmarc_status: str
    last_sync_at: datetime
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MailboxHealthResponse(BaseModel):
    mailbox_id: str
    email: str
    health_score: int
    status: str
    recommendations: List[str]
