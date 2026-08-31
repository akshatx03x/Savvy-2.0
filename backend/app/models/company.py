from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.lead import Lead


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    normalized_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    industry: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    employee_count_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_company_country_industry", "country", "industry"),
        Index("idx_company_norm_domain", "normalized_domain"),
        Index("idx_company_norm_name_country", "normalized_name", "country"),
    )
