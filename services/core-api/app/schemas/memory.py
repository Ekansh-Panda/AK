"""Memory schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedORMModel


class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1)
    namespace: str = "default"
    user_id: str | None = None
    meta: str | None = None


class MemoryOut(TimestampedORMModel):
    user_id: str | None = None
    namespace: str
    content: str
    meta: str | None = None


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    namespace: str = "default"
    limit: int = Field(10, ge=1, le=100)


class MemorySearchResult(BaseModel):
    memory: MemoryOut
    score: float = 0.0
