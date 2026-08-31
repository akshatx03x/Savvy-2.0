from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class ResearchProfile(Base, TimestampMixin):
    __tablename__ = "research_profiles"

    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)

    research_depth: Mapped[str] = mapped_column(String(20), nullable=False, default="standard") # basic, standard, deep
    intelligence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    business_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    products_services: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    online_presence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default={})

    recent_activity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    growth_signals: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    technology_signals: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    marketing_signals: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    hiring_signals: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])

    last_researched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    findings: Mapped[List["ResearchFinding"]] = relationship("ResearchFinding", back_populates="profile", cascade="all, delete-orphan")
    evidence_items: Mapped[List["ResearchEvidence"]] = relationship("ResearchEvidence", back_populates="profile", cascade="all, delete-orphan")
    signals: Mapped[List["ResearchSignal"]] = relationship("ResearchSignal", back_populates="profile", cascade="all, delete-orphan")
    opportunities: Mapped[List["ResearchOpportunity"]] = relationship("ResearchOpportunity", back_populates="profile", cascade="all, delete-orphan")
    personalization_angles: Mapped[List["PersonalizationAngle"]] = relationship("PersonalizationAngle", back_populates="profile", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_research_company_lead", "company_id", "lead_id"),
        Index("idx_research_score", "intelligence_score"),
    )


class ResearchFinding(Base, TimestampMixin):
    __tablename__ = "research_findings"

    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # COMPANY, PRODUCT, SERVICE, MARKETING, WEBSITE, SOCIAL, NEWS, GROWTH, HIRING, TECHNOLOGY, CONTENT, BUSINESS_SIGNAL, OTHER

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[str] = mapped_column(String(20), nullable=False, default="medium") # low, medium, high, critical
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.85, index=True)

    # Relationships
    profile: Mapped["ResearchProfile"] = relationship("ResearchProfile", back_populates="findings")
    evidence: Mapped[List["ResearchEvidence"]] = relationship("ResearchEvidence", back_populates="finding", cascade="all, delete-orphan")


class ResearchEvidence(Base, TimestampMixin):
    __tablename__ = "research_evidence"

    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("research_findings.id", ondelete="CASCADE"), nullable=True, index=True)

    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="website") # website, search, news, directory

    supporting_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recency_tier: Mapped[str] = mapped_column(String(20), nullable=False, default="fresh") # recent (0-30d), fresh (31-90d), moderate (91-365d), old (365d+)

    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)
    is_observation_vs_inference: Mapped[str] = mapped_column(String(20), nullable=False, default="observation") # observation, inference

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    profile: Mapped["ResearchProfile"] = relationship("ResearchProfile", back_populates="evidence_items")
    finding: Mapped[Optional["ResearchFinding"]] = relationship("ResearchFinding", back_populates="evidence")


class ResearchSignal(Base, TimestampMixin):
    __tablename__ = "research_signals"

    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    signal_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)
    recency_tier: Mapped[str] = mapped_column(String(20), nullable=False, default="recent")
    importance: Mapped[str] = mapped_column(String(20), nullable=False, default="high")

    # Relationships
    profile: Mapped["ResearchProfile"] = relationship("ResearchProfile", back_populates="signals")


class ResearchOpportunity(Base, TimestampMixin):
    __tablename__ = "research_opportunities"

    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    potential_offer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)

    observation_text: Mapped[str] = mapped_column(Text, nullable=False)
    inference_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    profile: Mapped["ResearchProfile"] = relationship("ResearchProfile", back_populates="opportunities")


class PersonalizationAngle(Base, TimestampMixin):
    __tablename__ = "personalization_angles"

    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    angle_title: Mapped[str] = mapped_column(String(255), nullable=False)
    angle_reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)

    # Relationships
    profile: Mapped["ResearchProfile"] = relationship("ResearchProfile", back_populates="personalization_angles")
