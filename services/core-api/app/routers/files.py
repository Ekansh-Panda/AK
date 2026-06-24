"""File upload / metadata endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import StatusResponse
from app.schemas.file import FileOut
from app.services.files.service import FileIngestionService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", response_model=FileOut)
async def upload_file(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> FileOut:
    service = FileIngestionService(db)
    data = await file.read()
    record = service.register_upload(
        file.filename or "upload.bin",
        data,
        content_type=file.content_type,
    )
    return FileOut.model_validate(record)


@router.get("", response_model=list[FileOut])
def list_files(db: Session = Depends(get_db)) -> list[FileOut]:
    service = FileIngestionService(db)
    return [FileOut.model_validate(r) for r in service.list()]


@router.get("/{file_id}", response_model=FileOut)
def get_file(file_id: str, db: Session = Depends(get_db)) -> FileOut:
    service = FileIngestionService(db)
    record = service.get(file_id)
    if not record:
        raise HTTPException(status_code=404, detail="file not found")
    return FileOut.model_validate(record)


@router.delete("/{file_id}", response_model=StatusResponse)
def delete_file(file_id: str, db: Session = Depends(get_db)) -> StatusResponse:
    service = FileIngestionService(db)
    if not service.delete(file_id):
        raise HTTPException(status_code=404, detail="file not found")
    return StatusResponse(detail="deleted")
