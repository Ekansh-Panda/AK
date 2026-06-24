"""Provider registry and default selection."""

from __future__ import annotations

from app.core.logging import get_logger
from app.services.providers.base import ModelProvider
from app.services.providers.mock_provider import MockProvider

logger = get_logger(__name__)


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}
        self._default: str | None = None

    def register(self, provider: ModelProvider, *, default: bool = False) -> None:
        self._providers[provider.name] = provider
        if default or self._default is None:
            self._default = provider.name

    def get(self, name: str | None = None) -> ModelProvider:
        key = name or self._default
        if key is None or key not in self._providers:
            raise KeyError(f"No provider registered for '{name}'")
        return self._providers[key]

    def list(self) -> list[ModelProvider]:
        return list(self._providers.values())

    @property
    def default_name(self) -> str | None:
        return self._default


# Process-wide default registry, pre-loaded with the offline mock provider.
# TODO(Odysseus): register real providers at startup based on config/secrets.
registry = ProviderRegistry()
registry.register(MockProvider(), default=True)
