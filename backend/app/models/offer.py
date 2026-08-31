from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin


class OfferProfile(Base, TimestampMixin):
    __tablename__ = "offer_profiles"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_customer: Mapped[str] = mapped_column(String(255), nullable=False)
    value_proposition: Mapped[str] = mapped_column(Text, nullable=False)

    differentiators: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cta: Mapped[str] = mapped_column(String(255), nullable=False, default="Would you be open to a 15-minute call?")
    tone_preferences: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Consultative")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    __table_args__ = (
        Index("idx_offer_active", "is_active"),
    )
