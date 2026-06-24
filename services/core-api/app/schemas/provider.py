"""Provider schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    context_window: int | None = None


class ProviderInfo(BaseModel):
    name: str
    description: str
    available: bool = True
    models: list[ModelInfo] = []
