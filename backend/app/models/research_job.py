from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Text, JSON, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class ResearchJob(Base, TimestampMixin):
    __tablename__ = "research_jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    research_depth: Mapped[str] = mapped_column(String(20), nullable=False, default="standard") # basic, standard, deep
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED", index=True)
    # QUEUED, IDENTIFYING, DISCOVERING, FETCHING, ANALYZING, EXTRACTING, SCORING, FINALIZING, COMPLETED, PARTIAL, FAILED, CANCELLED

    total_leads: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    partial_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    target_lead_ids: Mapped[dict] = mapped_column(JSON, nullable=False, default=[])

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    logs: Mapped[List["ResearchJobLog"]] = relationship("ResearchJobLog", back_populates="job", cascade="all, delete-orphan")


class ResearchJobLog(Base, TimestampMixin):
    __tablename__ = "research_job_logs"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lead_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    job: Mapped["ResearchJob"] = relationship("ResearchJob", back_populates="logs")
