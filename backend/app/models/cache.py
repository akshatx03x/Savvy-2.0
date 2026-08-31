from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin


class URLContentCache(Base, TimestampMixin):
    __tablename__ = "url_content_cache"

    url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    http_status: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, default="website")

    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
