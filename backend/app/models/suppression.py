from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin


class SuppressionEntry(Base, TimestampMixin):
    __tablename__ = "suppression_list"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    reason: Mapped[str] = mapped_column(String(50), nullable=False, default="OPT_OUT") # OPT_OUT, HARD_BOUNCE, COMPLAINT, MANUAL, INVALID_ADDRESS
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="system")

    __table_args__ = (
        Index("idx_suppression_email", "email"),
    )
