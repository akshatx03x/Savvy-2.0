from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default={})
