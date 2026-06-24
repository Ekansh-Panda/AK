"""Default lite memory provider backed by SQLite.

Uses simple substring matching for ``search`` — good enough for v0.1 and keeps
Miori usable on low-end machines without embeddings.

TODO(Odysseus/Khoj): replace substring search with semantic vector retrieval
when LITE_MODE is off.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.services.memory.base import MemoryItem, MemoryProvider


def _to_item(row: Memory, score: float = 0.0) -> MemoryItem:
    return MemoryItem(
        id=row.id,
        namespace=row.namespace,
        content=row.content,
        user_id=row.user_id,
        meta=row.meta,
        score=score,
    )


class SqliteMemoryProvider(MemoryProvider):
    name = "sqlite-lite"

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(
        self,
        content: str,
        *,
        namespace: str = "default",
        user_id: str | None = None,
        meta: str | None = None,
    ) -> MemoryItem:
        row = Memory(
            content=content, namespace=namespace, user_id=user_id, meta=meta
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return _to_item(row)

    def search(
        self, query: str, *, namespace: str = "default", limit: int = 10
    ) -> list[MemoryItem]:
        stmt = (
            select(Memory)
            .where(Memory.namespace == namespace)
            .where(Memory.content.ilike(f"%{query}%"))
            .limit(limit)
        )
        rows = self._db.execute(stmt).scalars().all()
        # Naive score: 1.0 for any match. TODO: real relevance scoring.
        return [_to_item(r, score=1.0) for r in rows]

    def list(self, *, limit: int = 50) -> list[MemoryItem]:
        stmt = select(Memory).order_by(Memory.created_at.desc()).limit(limit)
        rows = self._db.execute(stmt).scalars().all()
        return [_to_item(r) for r in rows]

    def get(self, memory_id: str) -> MemoryItem | None:
        row = self._db.get(Memory, memory_id)
        return _to_item(row) if row else None

    def delete(self, memory_id: str) -> bool:
        row = self._db.get(Memory, memory_id)
        if not row:
            return False
        self._db.delete(row)
        self._db.commit()
        return True
