"""MemoryService — wires a concrete MemoryProvider to the rest of the app.

Selects the provider based on config (lite vs heavy). For now only the SQLite
lite provider exists.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.services.memory.base import MemoryItem, MemoryProvider
from app.services.memory.sqlite_memory import SqliteMemoryProvider

logger = get_logger(__name__)


class MemoryService:
    def __init__(self, db: Session, provider: MemoryProvider | None = None) -> None:
        self._db = db
        self._provider = provider or self._select_provider(db)

    @staticmethod
    def _select_provider(db: Session) -> MemoryProvider:
        if settings.LITE_MODE:
            return SqliteMemoryProvider(db)
        # TODO(Odysseus/Khoj): return a vector-backed provider here.
        logger.info("LITE_MODE off but no heavy provider wired; using sqlite-lite")
        return SqliteMemoryProvider(db)

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def add(
        self,
        content: str,
        *,
        namespace: str = "default",
        user_id: str | None = None,
        meta: str | None = None,
    ) -> MemoryItem:
        return self._provider.add(
            content, namespace=namespace, user_id=user_id, meta=meta
        )

    def search(
        self, query: str, *, namespace: str = "default", limit: int = 10
    ) -> list[MemoryItem]:
        return self._provider.search(query, namespace=namespace, limit=limit)

    def list(self, *, limit: int = 50) -> list[MemoryItem]:
        return self._provider.list(limit=limit)

    def get(self, memory_id: str) -> MemoryItem | None:
        return self._provider.get(memory_id)

    def delete(self, memory_id: str) -> bool:
        return self._provider.delete(memory_id)
