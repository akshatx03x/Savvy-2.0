from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.lead import Lead
    from app.models.source import LeadSourceProvenance


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    
    job_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    normalized_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    normalized_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="web")
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unverified") # verified, unverified, invalid
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="contacts")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="contact", cascade="all, delete-orphan")
    sources: Mapped[List["LeadSourceProvenance"]] = relationship("LeadSourceProvenance", back_populates="contact", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_contact_norm_email", "normalized_email"),
        Index("idx_contact_norm_phone", "normalized_phone"),
        Index("idx_contact_company_name", "company_id", "full_name"),
    )
