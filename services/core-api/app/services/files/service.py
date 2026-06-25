"""FileIngestionService — store uploaded files, extract text, track metadata.

Files are written under ``settings.UPLOAD_DIR``. On upload we best-effort
extract text for common text/code formats and PDFs (pypdf, lazy-imported). PDF
extraction degrades gracefully when pypdf is absent (lite-mode) — we store a
note and keep the upload.
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

# Extensions decoded directly as UTF-8 text (errors='replace').
TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".json",
    ".csv",
    ".log",
    # common code
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".rs",
    ".go",
    ".java",
}


class UploadTooLargeError(Exception):
    """Raised when an upload exceeds ``settings.MAX_UPLOAD_BYTES``."""

    def __init__(self, size: int, limit: int) -> None:
        self.size = size
        self.limit = limit
        super().__init__(f"upload of {size} bytes exceeds limit of {limit} bytes")


class FileIngestionService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._upload_dir = Path(settings.UPLOAD_DIR)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    # --- extraction ---
    @staticmethod
    def _extract_text(filename: str, data: bytes) -> tuple[str | None, str]:
        """Return (extracted_text, status). status is "ingested" or "uploaded"."""
        ext = Path(filename).suffix.lower()
        if ext in TEXT_EXTENSIONS:
            return data.decode("utf-8", errors="replace"), "ingested"
        if ext == ".pdf":
            return FileIngestionService._extract_pdf(data)
        # Unknown/binary: keep as-is, no text.
        return None, "uploaded"

    @staticmethod
    def _extract_pdf(data: bytes) -> tuple[str | None, str]:
        try:
            import io

            import pypdf  # lazy / optional
        except ImportError:
            logger.info("pypdf not installed; storing PDF without text extraction")
            return "[pdf text extraction unavailable: pypdf not installed]", "uploaded"
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            return text.strip() or None, "ingested"
        except Exception as exc:  # noqa: BLE001 - never crash on bad PDFs
            logger.warning("PDF extraction failed: %s", exc)
            return f"[pdf text extraction failed: {exc}]", "failed"

    # --- ingestion ---
    def register_upload(
        self,
        filename: str,
        data: bytes,
        *,
        content_type: str | None = None,
        user_id: str | None = None,
    ) -> FileRecord:
        """Persist bytes to disk, extract text, and record metadata.

        Raises ``UploadTooLargeError`` if the payload exceeds the configured max.
        """
        if len(data) > settings.MAX_UPLOAD_BYTES:
            raise UploadTooLargeError(len(data), settings.MAX_UPLOAD_BYTES)

        safe_name = Path(filename).name or "upload.bin"
        stored_name = f"{uuid.uuid4()}_{safe_name}"
        path = self._upload_dir / stored_name
        path.write_bytes(data)

        extracted, status = self._extract_text(safe_name, data)

        record = FileRecord(
            filename=safe_name,
            content_type=content_type,
            size_bytes=len(data),
            storage_path=str(path),
            status=status,
            user_id=user_id,
            extracted_text=extracted,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        logger.info(
            "Registered upload %s (%d bytes, status=%s)", safe_name, len(data), status
        )
        return record

    async def ingest(self, file_id: str) -> FileRecord:
        record = self._db.get(FileRecord, file_id)
        if not record:
            raise ValueError("file not found")

        from app.core.config import get_effective_bool
        from app.core.config import settings

        semantic_enabled = get_effective_bool(self._db, "semantic_memory_enabled", settings.SEMANTIC_MEMORY_ENABLED)
        if not semantic_enabled:
            raise ValueError("Semantic memory disabled")

        if record.status == "ingested":
            return record

        if not record.extracted_text:
            raise ValueError("no text to ingest")

        text = record.extracted_text
        words = text.split()
        chunk_size = 500
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        from app.services.memory.service import MemoryService
        mem = MemoryService(self._db)
        
        for idx, chunk in enumerate(chunks):
            await mem.add(chunk, namespace=f"file:{file_id}", meta=f"chunk {idx+1}/{len(chunks)}")
        
        record.status = "ingested"
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
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
