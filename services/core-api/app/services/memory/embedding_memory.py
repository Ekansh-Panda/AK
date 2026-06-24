"""Semantic memory provider (sentence-transformers + cosine similarity).

Used when LITE_MODE is off. Embeddings are computed with all-MiniLM-L6-v2 and
stored as a JSON float array on ``memories.embedding``; search embeds the query
and ranks candidates by cosine similarity in pure Python (numpy).

Both ``sentence-transformers`` and ``numpy`` are imported lazily. The model is
loaded once at construction so MemoryService._select_provider's guard can catch
a missing dependency and fall back to the SQLite-lite provider — Miori never
breaks on a low-end box.

Inherits list/get/update/delete from SqliteMemoryProvider; only add/search change.
"""

from __future__ import annotations

import json
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.memory import Memory
from app.services.memory.base import MemoryItem
from app.services.memory.sqlite_memory import SqliteMemoryProvider, _to_item

logger = get_logger(__name__)


@lru_cache(maxsize=2)
def _load_model(model_name: str):
    """Load (and cache) the sentence-transformers model. Raises if missing."""
    from sentence_transformers import SentenceTransformer  # lazy, heavy

    logger.info("Loading embedding model %s", model_name)
    return SentenceTransformer(model_name)


class EmbeddingMemoryProvider(SqliteMemoryProvider):
    name = "embedding"

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self._model_name = settings.EMBEDDING_MODEL
        # Eagerly load so a missing dependency surfaces here (caught by the
        # provider selector, which then falls back to sqlite-lite).
        self._model = _load_model(self._model_name)

    # --- embedding helpers ---
    def _embed_one(self, text: str) -> list[float]:
        vec = self._model.encode([text], normalize_embeddings=True)[0]
        return [float(x) for x in vec]

    # --- writes ---
    def add(
        self,
        content: str,
        *,
        namespace: str = "default",
        user_id: str | None = None,
        meta: str | None = None,
        pinned: bool = False,
    ) -> MemoryItem:
        embedding = None
        try:
            embedding = json.dumps(self._embed_one(content))
        except Exception as exc:  # noqa: BLE001 - never block a write on embed
            logger.warning("embed on add failed: %s", exc)
        row = Memory(
            content=content,
            namespace=namespace,
            user_id=user_id,
            meta=meta,
            pinned=pinned,
            embedding=embedding,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return _to_item(row)

    # --- semantic search ---
    def search(
        self, query: str, *, namespace: str = "default", limit: int = 10
    ) -> list[MemoryItem]:
        import numpy as np  # lazy

        rows = list(
            self._db.execute(
                select(Memory).where(Memory.namespace == namespace)
            ).scalars()
        )
        if not rows:
            return []

        try:
            q = np.asarray(self._embed_one(query), dtype="float32")
        except Exception as exc:  # noqa: BLE001 - degrade to substring
            logger.warning("query embed failed (%s); substring fallback", exc)
            return super().search(query, namespace=namespace, limit=limit)

        scored: list[tuple[float, Memory]] = []
        for r in rows:
            if not r.embedding:
                continue
            try:
                v = np.asarray(json.loads(r.embedding), dtype="float32")
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            denom = float(np.linalg.norm(q) * np.linalg.norm(v))
            if denom == 0.0:
                continue
            scored.append((float(np.dot(q, v) / denom), r))

        if not scored:
            # Nothing embedded yet (e.g. pre-existing lite rows) — substring.
            return super().search(query, namespace=namespace, limit=limit)

        scored.sort(key=lambda t: t[0], reverse=True)
        return [_to_item(r, score=s) for s, r in scored[:limit]]
