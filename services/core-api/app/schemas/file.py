"""File schemas."""

from __future__ import annotations

from app.schemas.common import TimestampedORMModel


class FileOut(TimestampedORMModel):
    user_id: str | None = None
    filename: str
    content_type: str | None = None
    size_bytes: int
    # NOTE: ``storage_path`` is intentionally NOT exposed here — it leaks the
    # server filesystem layout. The ORM model keeps it for internal use.
    status: str
