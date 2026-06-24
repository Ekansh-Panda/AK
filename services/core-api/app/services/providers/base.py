"""Model provider abstraction.

A provider talks to an LLM backend. The mock provider lets chat work fully
offline. Real providers plug in behind the same interface.

TODO(Odysseus): wire real providers (local + hosted LLMs) and a router that
picks a model per persona mode / task.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str


@dataclass
class ModelDescriptor:
    id: str
    name: str
    provider: str
    context_window: int | None = None


class ModelProvider(ABC):
    """Interface every model backend must implement."""

    name: str = "base"

    def available(self) -> bool:
        """Whether this provider is usable right now (e.g. API key present).

        Defaults to True so offline providers (mock) are always available. Real
        providers override this to report missing credentials without crashing.
        """
        return True

    @abstractmethod
    def list_models(self) -> list[ModelDescriptor]:
        """Return the models this provider exposes."""

    @abstractmethod
    async def chat(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Return a single completion string."""

    @abstractmethod
    async def stream(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Yield completion tokens/chunks as they are produced."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for ``texts``. Optional capability.

        Defaults to NotImplementedError so callers can probe and fall back (e.g.
        to a local sentence-transformers model) without crashing.
        """
        raise NotImplementedError(f"{self.name} provider does not support embeddings")
