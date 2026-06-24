"""FileIngestionService — store uploaded files and track metadata.

Files are written under ``settings.UPLOAD_DIR``. Ingestion (parsing/embedding)
is deferred.

TODO(Khoj/Odysseus): add a background ingestion pipeline that parses content
and indexes it into the memory/vector store after upload.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.file import FileRecord

logger = get_logger(__name__)


class FileIngestionService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._upload_dir = Path(settings.UPLOAD_DIR)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    def register_upload(
        self,
        filename: str,
        data: bytes,
        *,
        content_type: str | None = None,
        user_id: str | None = None,
    ) -> FileRecord:
        """Persist bytes to disk and record metadata."""
        safe_name = Path(filename).name or "upload.bin"
        stored_name = f"{uuid.uuid4()}_{safe_name}"
        path = self._upload_dir / stored_name
        path.write_bytes(data)

        record = FileRecord(
            filename=safe_name,
            content_type=content_type,
            size_bytes=len(data),
            storage_path=str(path),
            status="uploaded",
            user_id=user_id,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        logger.info("Registered upload %s (%d bytes)", safe_name, len(data))
        # TODO: enqueue ingestion job here.
        return record

    def list(self) -> list[FileRecord]:
        return list(self._db.execute(select(FileRecord)).scalars().all())

    def get(self, file_id: str) -> FileRecord | None:
        return self._db.get(FileRecord, file_id)

    def delete(self, file_id: str) -> bool:
        record = self._db.get(FileRecord, file_id)
        if not record:
            return False
        try:
            Path(record.storage_path).unlink(missing_ok=True)
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("Could not delete file %s: %s", record.storage_path, exc)
        self._db.delete(record)
        self._db.commit()
        return True
