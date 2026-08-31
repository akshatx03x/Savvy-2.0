from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class OutreachDraft(Base, TimestampMixin):
    __tablename__ = "outreach_drafts"

    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    offer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("offer_profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    objective: Mapped[str] = mapped_column(String(100), nullable=False, default="Book a meeting")
    tone: Mapped[str] = mapped_column(String(50), nullable=False, default="Consultative")
    length: Mapped[str] = mapped_column(String(50), nullable=False, default="Short")
    personalization_level: Mapped[str] = mapped_column(String(50), nullable=False, default="DEEP") # MINIMAL, STANDARD, DEEP
    cta_type: Mapped[str] = mapped_column(String(100), nullable=False, default="Soft CTA")

    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    preview_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    ps_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    personalization_score: Mapped[int] = mapped_column(Integer, nullable=False, default=90, index=True)
    evidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=92)
    relevance_score: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    naturalness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=88)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True) # DRAFT, APPROVED, ARCHIVED, NEEDS_RESEARCH
    unsupported_claims: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])
    message_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default={})
    evidence_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=[])

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    versions: Mapped[List["OutreachDraftVersion"]] = relationship("OutreachDraftVersion", back_populates="draft", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_outreach_lead_status", "lead_id", "status"),
        Index("idx_outreach_score", "personalization_score"),
    )


class OutreachDraftVersion(Base, TimestampMixin):
    __tablename__ = "outreach_draft_versions"

    draft_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach_drafts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    personalization_score: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    change_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    draft: Mapped["OutreachDraft"] = relationship("OutreachDraft", back_populates="versions")
