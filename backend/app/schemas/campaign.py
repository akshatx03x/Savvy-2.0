from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.mailbox import MailboxResponse


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    contact_ids: List[str] = Field(..., min_length=1)
    mailbox_ids: List[str] = Field(..., min_length=1)
    timezone: str = "UTC"
    schedule_config: Optional[Dict[str, Any]] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    timezone: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None


class CampaignRecipientResponse(BaseModel):
    id: str
    campaign_id: str
    contact_id: str
    mailbox_id: Optional[str] = None
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    error_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignMessageResponse(BaseModel):
    id: str
    campaign_recipient_id: str
    outreach_draft_id: str
    subject: str
    body: str
    provider_message_id: Optional[str] = None
    status: str
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    reply_category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    timezone: str
    schedule_config: Dict[str, Any]
    total_recipients: int
    sent_count: int
    delivered_count: int
    opened_count: int
    replied_count: int
    positive_replied_count: int
    bounced_count: int
    complaint_count: int
    opt_out_count: int
    mailbox_ids: List[str] = Field(default_factory=list)
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignReviewResponse(BaseModel):
    campaign_name: str
    total_recipients: int
    approved_messages_count: int
    missing_outreach_count: int
    suppressed_count: int
    invalid_count: int
    selected_mailboxes_count: int
    total_daily_capacity: int
    warnings: List[str]
    can_launch: bool
