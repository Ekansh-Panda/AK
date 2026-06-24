"""Provider listing endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.provider import ModelInfo, ProviderInfo
from app.services.providers.registry import registry

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=list[ProviderInfo])
def list_providers() -> list[ProviderInfo]:
    out: list[ProviderInfo] = []
    for provider in registry.list():
        models = [
            ModelInfo(
                id=m.id,
                name=m.name,
                provider=m.provider,
                context_window=m.context_window,
            )
            for m in provider.list_models()
        ]
        out.append(
            ProviderInfo(
                name=provider.name,
                description=f"{provider.name} model provider",
                available=True,
                models=models,
            )
        )
    return out


@router.get("/models", response_model=list[ModelInfo])
def list_models() -> list[ModelInfo]:
    models: list[ModelInfo] = []
    for provider in registry.list():
        for m in provider.list_models():
            models.append(
                ModelInfo(
                    id=m.id,
                    name=m.name,
                    provider=m.provider,
                    context_window=m.context_window,
                )
            )
    return models
