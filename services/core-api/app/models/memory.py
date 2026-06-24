"""Memory record model.

A lightweight key/text store for the default lite memory provider. Vector
embeddings are intentionally optional.

TODO(Odysseus/Khoj): add an embedding column / external vector store reference
when the heavy memory providers are wired in.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Memory(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "memories"

    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    # Logical grouping, e.g. "facts", "preferences", "projects".
    namespace: Mapped[str] = mapped_column(String(64), default="default", index=True)
    content: Mapped[str] = mapped_column(Text)
    # Free-form JSON-ish metadata serialized as text to stay SQLite-friendly.
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)
