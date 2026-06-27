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

    # Sentinel so subclasses can pass an explicit ``None`` key (= unconfigured)
    # without silently inheriting OPENAI_API_KEY.
    _UNSET = object()

    def __init__(
        self,
        *,
        api_key: object = _UNSET,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = (
            settings.OPENAI_API_KEY if api_key is self._UNSET else api_key  # type: ignore[assignment]
        )
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
        tools: list[dict] | None = None,
    ) -> dict:
        wire: list[dict] = []
        if system_prompt:
            wire.append({"role": "system", "content": system_prompt})
        for m in messages:
            role = m.role if m.role in ("system", "user", "assistant", "tool") else "user"
            msg_dict = {"role": role, "content": m.content or ""}
            if m.tool_calls:
                msg_dict["tool_calls"] = m.tool_calls
            if m.tool_call_id:
                msg_dict["tool_call_id"] = m.tool_call_id
            wire.append(msg_dict)
            
        payload = {
            "model": model or self._model,
            "messages": wire,
            "stream": stream,
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
        return payload

    # --- inference ---
    async def chat(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> str | ChatMessage:
        if not self.available():
            raise RuntimeError("OpenAI provider unavailable: missing OPENAI_API_KEY")
        import httpx  # lazy

        payload = self._payload(
            messages, model=model, system_prompt=system_prompt, stream=False, tools=tools
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            
        choice = data["choices"][0]["message"]
        if choice.get("tool_calls"):
            return ChatMessage(role="assistant", content=choice.get("content"), tool_calls=choice["tool_calls"])
            
        return choice.get("content") or ""

    async def stream(
        self,
        messages: Iterable[ChatMessage],
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[str | ChatMessage]:
        if not self.available():
            raise RuntimeError("OpenAI provider unavailable: missing OPENAI_API_KEY")
        import httpx  # lazy

        payload = self._payload(
            messages, model=model, system_prompt=system_prompt, stream=True, tools=tools
        )
        
        tool_calls_buffer = {}
        content_buffer = []

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
                        
                        # Handle tool calls in stream
                        if "tool_calls" in delta:
                            for tc in delta["tool_calls"]:
                                idx = tc["index"]
                                if idx not in tool_calls_buffer:
                                    tool_calls_buffer[idx] = tc
                                else:
                                    if "function" in tc:
                                        if "arguments" in tc["function"]:
                                            tool_calls_buffer[idx]["function"]["arguments"] += tc["function"]["arguments"]
                        
                        token = delta.get("content")
                        if token:
                            content_buffer.append(token)
                            yield token
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

        if tool_calls_buffer:
            yield ChatMessage(
                role="assistant",
                content="".join(content_buffer) if content_buffer else None,
                tool_calls=[tc for tc in tool_calls_buffer.values()]
            )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.available():
            raise RuntimeError("OpenAI provider unavailable: missing OPENAI_API_KEY")
        import httpx  # lazy

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/embeddings",
                headers=self._headers(),
                json={"model": "text-embedding-3-small", "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
        return [row["embedding"] for row in data.get("data", [])]

    # Alias to match callers that expect chat_stream().
    chat_stream = stream
