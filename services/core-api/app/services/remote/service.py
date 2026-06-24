"""RemoteSessionService — device registry and remote control sessions.

Devices are persisted in the DB; live remote sessions are tracked in-memory for
v0.1. This is a stub for the remote dashboard wiring.

TODO(Mark-XLVI): replace the in-memory session map with a real transport
(secure relay / WebRTC / signaling) and add pairing + auth.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.device import Device

logger = get_logger(__name__)


class RemoteSession:
    """Lightweight in-memory remote session record."""

    def __init__(self, device_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.device_id = device_id
        self.state = "active"
        self.created_at = datetime.now(timezone.utc)


class RemoteSessionService:
    # Class-level so sessions survive across request-scoped instances.
    _sessions: dict[str, RemoteSession] = {}

    def __init__(self, db: Session) -> None:
        self._db = db

    # --- devices ---
    def register_device(
        self, name: str, platform: str | None = None, user_id: str | None = None
    ) -> Device:
        device = Device(
            name=name, platform=platform, user_id=user_id, state="online"
        )
        device.last_seen_at = datetime.now(timezone.utc)
        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        return device

    def list_devices(self) -> list[Device]:
        return list(self._db.execute(select(Device)).scalars().all())

    def set_device_state(self, device_id: str, state: str) -> Device | None:
        """Set state to one of online/offline/sleeping (wake/sleep)."""
        device = self._db.get(Device, device_id)
        if not device:
            return None
        device.state = state
        device.last_seen_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(device)
        return device

    # --- sessions ---
    def create_session(self, device_id: str) -> RemoteSession:
        session = RemoteSession(device_id)
        self._sessions[session.id] = session
        logger.info("Remote session %s created for device %s", session.id, device_id)
        return session

    def list_sessions(self) -> list[RemoteSession]:
        return list(self._sessions.values())

    def end_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None
