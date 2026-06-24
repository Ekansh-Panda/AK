"""Memory REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import StatusResponse
from app.schemas.memory import (
    MemoryCreate,
    MemoryOut,
    MemorySearchRequest,
    MemorySearchResult,
)
from app.services.memory.service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("", response_model=MemoryOut)
def add_memory(body: MemoryCreate, db: Session = Depends(get_db)) -> MemoryOut:
    service = MemoryService(db)
    item = service.add(
        body.content,
        namespace=body.namespace,
        user_id=body.user_id,
        meta=body.meta,
    )
    # Re-fetch the ORM row for full timestamps.
    from app.models.memory import Memory

    row = db.get(Memory, item.id)
    return MemoryOut.model_validate(row)


@router.get("", response_model=list[MemoryOut])
def list_memory(limit: int = 50, db: Session = Depends(get_db)) -> list[MemoryOut]:
    service = MemoryService(db)
    from app.models.memory import Memory

    out: list[MemoryOut] = []
    for item in service.list(limit=limit):
        row = db.get(Memory, item.id)
        if row:
            out.append(MemoryOut.model_validate(row))
    return out


@router.post("/search", response_model=list[MemorySearchResult])
def search_memory(
    body: MemorySearchRequest, db: Session = Depends(get_db)
) -> list[MemorySearchResult]:
    service = MemoryService(db)
    from app.models.memory import Memory

    results: list[MemorySearchResult] = []
    for item in service.search(body.query, namespace=body.namespace, limit=body.limit):
        row = db.get(Memory, item.id)
        if row:
            results.append(
                MemorySearchResult(
                    memory=MemoryOut.model_validate(row), score=item.score
                )
            )
    return results


@router.get("/{memory_id}", response_model=MemoryOut)
def get_memory(memory_id: str, db: Session = Depends(get_db)) -> MemoryOut:
    from app.models.memory import Memory

    row = db.get(Memory, memory_id)
    if not row:
        raise HTTPException(status_code=404, detail="memory not found")
    return MemoryOut.model_validate(row)


@router.delete("/{memory_id}", response_model=StatusResponse)
def delete_memory(memory_id: str, db: Session = Depends(get_db)) -> StatusResponse:
    service = MemoryService(db)
    if not service.delete(memory_id):
        raise HTTPException(status_code=404, detail="memory not found")
    return StatusResponse(detail="deleted")
