from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.job import GenerationJob


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    industry: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    
    lead_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new", index=True) # new, contacted, qualified, unqualified, archived
    
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="web")
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    generation_job_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("generation_jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="leads", lazy="selectin")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="leads", lazy="selectin")
    generation_job: Mapped[Optional["GenerationJob"]] = relationship("GenerationJob", back_populates="leads")

    __table_args__ = (
        Index("idx_lead_country_industry", "country", "industry"),
        Index("idx_lead_score_status", "lead_score", "status"),
        Index("idx_lead_country_score", "country", "lead_score"),
    )
