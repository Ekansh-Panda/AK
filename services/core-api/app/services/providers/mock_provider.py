"""Offline mock model provider.

Echoes the last user message back with a friendly Miori-flavored wrapper and
streams it token-by-token so the WebSocket chat path works without any real
model or network access.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable

from app.services.providers.base import ChatMessage, ModelDescriptor, ModelProvider


class MockProvider(ModelProvider):
    name = "mock"

    def list_models(self) -> list[ModelDescriptor]:
        return [
            ModelDescriptor(
                id="mock-echo",
                name="Miori Mock Echo",
                provider=self.name,
                context_window=8192,
            )
        ]

    def _compose_reply(self, messages: Iterable[ChatMessage]) -> str:
        last_user = ""
        for m in messages:
            if m.role == "user":
                last_user = m.content
        if not last_user:
            return "Hey, I'm here. What's on your mind?"
        return f"(mock) I heard you say: {last_user}"

    async def chat(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        return self._compose_reply(list(messages))

    async def stream(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        reply = self._compose_reply(list(messages))
        for token in reply.split(" "):
            await asyncio.sleep(0.02)  # simulate generation latency
            yield token + " "
