from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)
    # DRAFT, SCHEDULED, ACTIVE, PAUSED, COMPLETED, CANCELLED, FAILED

    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="UTC")
    schedule_config: Mapped[dict] = mapped_column(JSON, nullable=False, default={
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "start_hour": "09:00",
        "end_hour": "17:00",
        "daily_limit": 150,
        "min_delay_seconds": 60,
    })

    total_recipients: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opened_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    replied_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    positive_replied_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bounced_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    complaint_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opt_out_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    mailbox_ids: Mapped[dict] = mapped_column(JSON, nullable=False, default=[])
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    recipients: Mapped[List["CampaignRecipient"]] = relationship("CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan")


class CampaignRecipient(Base, TimestampMixin):
    __tablename__ = "campaign_recipients"

    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    mailbox_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("mailboxes.id", ondelete="SET NULL"), nullable=True, index=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", index=True)
    # PENDING, SCHEDULED, SENDING, SENT, FAILED, BLOCKED_SUPPRESSED, BLOCKED_NO_OUTREACH, BLOCKED_QUOTA

    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="recipients")
    messages: Mapped[List["CampaignMessage"]] = relationship("CampaignMessage", back_populates="recipient", cascade="all, delete-orphan")


class CampaignMessage(Base, TimestampMixin):
    __tablename__ = "campaign_messages"

    campaign_recipient_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaign_recipients.id", ondelete="CASCADE"), nullable=False, index=True)
    outreach_draft_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach_drafts.id", ondelete="CASCADE"), nullable=False, index=True)

    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="SENT", index=True)
    # SENT, DELIVERED, OPENED, REPLIED, BOUNCED, COMPLAINT, UNSUBSCRIBED

    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    bounced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    reply_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # INTERESTED, NOT_INTERESTED, QUESTION, OUT_OF_OFFICE, UNSUBSCRIBE, OTHER

    # Relationships
    recipient: Mapped["CampaignRecipient"] = relationship("CampaignRecipient", back_populates="messages")
