"""Memory create + list + filter + pin, all offline against in-memory SQLite."""

from __future__ import annotations

from app.services.memory.service import MemoryService


def test_create_and_list(db):
    svc = MemoryService(db)
    svc.add("the sky is blue", namespace="facts")
    svc.add("user likes tea", namespace="preferences")

    items = svc.list(limit=10)
    contents = {i.content for i in items}
    assert "the sky is blue" in contents
    assert "user likes tea" in contents


def test_list_filter_by_kind(db):
    svc = MemoryService(db)
    svc.add("a fact", namespace="facts")
    svc.add("a pref", namespace="preferences")

    facts = svc.list(kind="facts")
    assert len(facts) == 1
    assert facts[0].namespace == "facts"


def test_pin_via_update_and_filter(db):
    svc = MemoryService(db)
    item = svc.add("important", namespace="facts")
    assert item.pinned is False

    updated = svc.update(item.id, pinned=True)
    assert updated is not None and updated.pinned is True

    pinned = svc.list(pinned=True)
    assert [p.id for p in pinned] == [item.id]


def test_update_content(db):
    svc = MemoryService(db)
    item = svc.add("old", namespace="facts")
    updated = svc.update(item.id, content="new")
    assert updated is not None and updated.content == "new"
