"""Current-user resolution.

Stub for now: returns a single fixed local user id so the rest of the app can be
written against a real ``user_id`` dependency. Phase 5 (auth.py + security.py)
replaces ``get_current_user`` with JWT/device-token verification without changing
any call sites.
"""

from __future__ import annotations

# Stable local/dev user id. A real users row isn't required (SQLite doesn't
# enforce FKs by default), but ensure_dev_user() can create one if needed.
DEV_USER_ID = "00000000-0000-0000-0000-000000000001"


def get_current_user() -> str:
    """FastAPI dependency: the authenticated user's id.

    TODO(Phase 5): verify a JWT / device token and return the real user id.
    """
    return DEV_USER_ID
