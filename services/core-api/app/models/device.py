"""Remote device model.

TODO(Mark-XLVI): extend with auth tokens / pairing secrets for secure remote
control sessions.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Device(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "devices"

    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128))
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # "online" | "offline" | "sleeping"
    state: Mapped[str] = mapped_column(String(16), default="offline")
    is_paired: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
