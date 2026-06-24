"""OpenAI Chat Completions provider (REST via httpx).

Works against any OpenAI-compatible endpoint — the canonical OpenAI API,
OpenRouter, or a local server (llama.cpp, vLLM, LM Studio, Ollama's OpenAI
shim) — by pointing ``OPENAI_BASE_URL`` at it.

``httpx`` is imported lazily inside the request methods so the module (and the
whole app) imports cleanly in lite-mode where httpx is not installed. If the
API key is absent the provider reports ``available() is False`` and never
crashes the app.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterable

from app.core.config import settings
from app.core.logging import get_logger
from app.services.providers.base import ChatMessage, ModelDescriptor, ModelProvider

logger = get_logger(__name__)


class OpenAICompatibleProvider(ModelProvider):
    name = "openai"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.OPENAI_API_KEY
        self._base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self._model = model or settings.OPENAI_MODEL

    # --- availability ---
    def available(self) -> bool:
        return bool(self._api_key)

    def list_models(self) -> list[ModelDescriptor]:
        return [
            ModelDescriptor(
                id=self._model,
                name=self._model,
                provider=self.name,
                context_window=None,
            )
        ]

    # --- request helpers ---
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _payload(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None,
        system_prompt: str | None,
        stream: bool,
    ) -> dict:
        wire: list[dict[str, str]] = []
        if system_prompt:
            wire.append({"role": "system", "content": system_prompt})
        for m in messages:
            role = m.role if m.role in ("system", "user", "assistant") else "user"
            wire.append({"role": role, "content": m.content})
        return {
            "model": model or self._model,
            "messages": wire,
            "stream": stream,
        }

    # --- inference ---
    async def chat(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        if not self.available():
            raise RuntimeError("OpenAI provider unavailable: missing OPENAI_API_KEY")
        import httpx  # lazy

        payload = self._payload(
            messages, model=model, system_prompt=system_prompt, stream=False
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"] or ""

    async def stream(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        if not self.available():
            raise RuntimeError("OpenAI provider unavailable: missing OPENAI_API_KEY")
        import httpx  # lazy

        payload = self._payload(
            messages, model=model, system_prompt=system_prompt, stream=True
        )
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    chunk = line[len("data:") :].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        obj = json.loads(chunk)
                        delta = obj["choices"][0].get("delta", {})
                        token = delta.get("content")
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    if token:
                        yield token

    # Alias to match callers that expect chat_stream().
    chat_stream = stream
