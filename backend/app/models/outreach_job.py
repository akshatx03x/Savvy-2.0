from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Text, JSON, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class OutreachJob(Base, TimestampMixin):
    __tablename__ = "outreach_jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED", index=True)
    # QUEUED, PREPARING, SELECTING_EVIDENCE, GENERATING, VALIDATING, SAVING, COMPLETED, PARTIAL, FAILED, CANCELLED

    total_leads: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    needs_research_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    target_lead_ids: Mapped[dict] = mapped_column(JSON, nullable=False, default=[])
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default={})

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    logs: Mapped[List["OutreachJobLog"]] = relationship("OutreachJobLog", back_populates="job", cascade="all, delete-orphan")


class OutreachJobLog(Base, TimestampMixin):
    __tablename__ = "outreach_job_logs"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lead_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    job: Mapped["OutreachJob"] = relationship("OutreachJob", back_populates="logs")
