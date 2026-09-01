from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Text, JSON, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.lead import Lead


class GenerationJob(Base, TimestampMixin):
    __tablename__ = "generation_jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    search_type: Mapped[str] = mapped_column(String(50), nullable=False, default="ai") # ai, manual
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED", index=True) 
    # QUEUED, PLANNING, SEARCHING, PROCESSING, DEDUPLICATING, SAVING, COMPLETED, PARTIAL, FAILED, CANCELLED

    query_params: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    
    niche: Mapped[str] = mapped_column(String(150), nullable=False, default="General", index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Global", index=True)
    
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    discovered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicates_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    saved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diagnostic: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="generation_job", lazy="selectin")
    logs: Mapped[List["JobLog"]] = relationship("JobLog", back_populates="job", cascade="all, delete-orphan", lazy="selectin")


class JobLog(Base, TimestampMixin):
    __tablename__ = "job_logs"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO") # INFO, WARNING, ERROR
    message: Mapped[str] = mapped_column(Text, nullable=False)
    step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    job: Mapped["GenerationJob"] = relationship("GenerationJob", back_populates="logs")
