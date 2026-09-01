from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contact import Contact


class LeadSourceProvenance(Base, TimestampMixin):
    __tablename__ = "lead_source_provenance"

    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_identifier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unverified")
    
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    contact: Mapped["Contact"] = relationship("Contact", back_populates="sources")
