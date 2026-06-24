"""ChatService — orchestrates persona + provider + persistence for a turn.

Shared by the REST chat router and the /ws/chat WebSocket so both paths use the
same history, persona prompt and provider.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.message import Message
from app.models.session import ChatSession
from app.services.persona.service import PersonaService, persona_service
from app.services.providers.base import ChatMessage
from app.services.providers.registry import ProviderRegistry
from app.services.providers.registry import registry as provider_registry

logger = get_logger(__name__)

# Summarize a session after every N assistant turns (cheap, best-effort).
SUMMARIZE_EVERY = 10


class ChatService:
    def __init__(
        self,
        db: Session,
        *,
        providers: ProviderRegistry | None = None,
        persona: PersonaService | None = None,
    ) -> None:
        self._db = db
        self._providers = providers or provider_registry
        self._persona = persona or persona_service

    # --- sessions ---
    def get_or_create_session(
        self,
        session_id: str | None,
        *,
        persona_mode: str | None = None,
        user_id: str | None = None,
    ) -> ChatSession:
        if session_id:
            existing = self._db.get(ChatSession, session_id)
            if existing:
                return existing
        session = ChatSession(
            persona_mode=persona_mode or self._persona.active_mode,
            user_id=user_id,
        )
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)
        return session

    def history(self, session_id: str) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return list(self._db.execute(stmt).scalars().all())

    def _persist(self, session_id: str, role: str, content: str, model: str | None = None) -> Message:
        msg = Message(session_id=session_id, role=role, content=content, model=model)
        self._db.add(msg)
        self._db.commit()
        self._db.refresh(msg)
        return msg

    def _build_provider_messages(self, session_id: str, new_user_text: str) -> list[ChatMessage]:
        msgs = [
            ChatMessage(role=m.role, content=m.content)
            for m in self.history(session_id)
        ]
        msgs.append(ChatMessage(role="user", content=new_user_text))
        return msgs

    # --- turns ---
    async def respond(
        self,
        *,
        session_id: str | None,
        user_text: str,
        model: str | None = None,
        persona_mode: str | None = None,
        user_id: str | None = None,
    ) -> tuple[ChatSession, Message]:
        """Single-shot turn: persist user msg, get reply, persist + return it."""
        if persona_mode:
            self._persona.set_mode(persona_mode)
        session = self.get_or_create_session(
            session_id, persona_mode=persona_mode, user_id=user_id
        )
        self._persist(session.id, "user", user_text)
        provider = self._providers.get()
        msgs = self._build_provider_messages(session.id, user_text)
        system_prompt = self._persona.active_prompt()
        try:
            reply_text = await provider.chat(
                msgs, model=model, system_prompt=system_prompt
            )
        except Exception as exc:  # noqa: BLE001 - fall back to mock on failure
            logger.warning("Provider %s chat failed, using mock: %s", provider.name, exc)
            provider = self._providers.get("mock")
            reply_text = await provider.chat(msgs, system_prompt=system_prompt)
        reply = self._persist(session.id, "assistant", reply_text, model=provider.name)
        await self._maybe_summarize(session.id)
        return session, reply

    async def stream_response(
        self,
        *,
        session_id: str | None,
        user_text: str,
        model: str | None = None,
        persona_mode: str | None = None,
        user_id: str | None = None,
    ) -> AsyncIterator[tuple[str, str]]:
        """Yield ('session', session_id) once, then ('token', chunk) repeatedly.

        Persists the user message up front and the full assistant message at the
        end.
        """
        if persona_mode:
            self._persona.set_mode(persona_mode)
        session = self.get_or_create_session(
            session_id, persona_mode=persona_mode, user_id=user_id
        )
        self._persist(session.id, "user", user_text)
        yield ("session", session.id)

        provider = self._providers.get()
        msgs = self._build_provider_messages(session.id, user_text)
        system_prompt = self._persona.active_prompt()
        chunks: list[str] = []
        try:
            async for chunk in provider.stream(
                msgs, model=model, system_prompt=system_prompt
            ):
                chunks.append(chunk)
                yield ("token", chunk)
        except Exception as exc:  # noqa: BLE001 - degrade to mock mid-failure
            logger.warning(
                "Provider %s stream failed, using mock: %s", provider.name, exc
            )
            # Only fall back cleanly if nothing was streamed yet.
            if not chunks:
                provider = self._providers.get("mock")
                async for chunk in provider.stream(msgs, system_prompt=system_prompt):
                    chunks.append(chunk)
                    yield ("token", chunk)
            else:
                yield ("error", f"provider error: {exc}")

        self._persist(
            session.id, "assistant", "".join(chunks).strip(), model=provider.name
        )
        await self._maybe_summarize(session.id)
        yield ("done", session.id)

    # --- summarization hook ---
    async def _maybe_summarize(self, session_id: str) -> None:
        """Best-effort: every SUMMARIZE_EVERY assistant turns, store a summary.

        Swallows all errors so a failed summary never breaks a chat turn.
        """
        try:
            n_assistant = self._db.execute(
                select(func.count())
                .select_from(Message)
                .where(Message.session_id == session_id)
                .where(Message.role == "assistant")
            ).scalar_one()
            if n_assistant and n_assistant % SUMMARIZE_EVERY == 0:
                from app.services.memory.service import MemoryService

                await MemoryService(self._db).summarize_session(session_id)
        except Exception as exc:  # noqa: BLE001 - non-blocking, best-effort
            logger.debug("summarize hook skipped: %s", exc)
