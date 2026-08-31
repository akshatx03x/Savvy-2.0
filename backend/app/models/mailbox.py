from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin


class Mailbox(Base, TimestampMixin):
    __tablename__ = "mailboxes"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="gmail") # gmail, microsoft, smtp, simulated
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    provider_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    connection_status: Mapped[str] = mapped_column(String(50), nullable=False, default="CONNECTED", index=True) # CONNECTED, NEEDS_ATTENTION, DISCONNECTED
    encrypted_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    encrypted_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    daily_send_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    current_usage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    health_score: Mapped[int] = mapped_column(Integer, nullable=False, default=92, index=True)
    bounce_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.011) # 1.1%
    complaint_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0004) # 0.04%
    reply_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.082) # 8.2%

    spf_status: Mapped[str] = mapped_column(String(50), nullable=False, default="CONFIGURED") # CONFIGURED, NEEDS_ATTENTION, UNKNOWN
    dkim_status: Mapped[str] = mapped_column(String(50), nullable=False, default="CONFIGURED")
    dmarc_status: Mapped[str] = mapped_column(String(50), nullable=False, default="CONFIGURED")

    last_sync_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    __table_args__ = (
        Index("idx_mailbox_status_health", "connection_status", "health_score"),
    )
