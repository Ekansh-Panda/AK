"""Remote device + session endpoints.

TODO(Mark-XLVI): secure these with pairing/auth and a real remote transport.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.device import Device
from app.schemas.common import StatusResponse
from app.schemas.remote import (
    DeviceOut,
    DeviceRegister,
    RemoteSessionOut,
)
from app.services.remote.service import RemoteSessionService

router = APIRouter(prefix="/remote", tags=["remote"])


@router.post("/devices", response_model=DeviceOut)
def register_device(
    body: DeviceRegister, db: Session = Depends(get_db)
) -> DeviceOut:
    service = RemoteSessionService(db)
    device = service.register_device(
        body.name, platform=body.platform, user_id=body.user_id
    )
    return DeviceOut.model_validate(device)


@router.get("/devices", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db)) -> list[DeviceOut]:
    service = RemoteSessionService(db)
    return [DeviceOut.model_validate(d) for d in service.list_devices()]


@router.post("/devices/{device_id}/wake", response_model=DeviceOut)
def wake_device(device_id: str, db: Session = Depends(get_db)) -> DeviceOut:
    service = RemoteSessionService(db)
    device = service.set_device_state(device_id, "online")
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    return DeviceOut.model_validate(device)


@router.post("/devices/{device_id}/sleep", response_model=DeviceOut)
def sleep_device(device_id: str, db: Session = Depends(get_db)) -> DeviceOut:
    service = RemoteSessionService(db)
    device = service.set_device_state(device_id, "sleeping")
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    return DeviceOut.model_validate(device)


@router.post("/devices/{device_id}/sessions", response_model=RemoteSessionOut)
def create_session(device_id: str, db: Session = Depends(get_db)) -> RemoteSessionOut:
    service = RemoteSessionService(db)
    if not db.get(Device, device_id):
        raise HTTPException(status_code=404, detail="device not found")
    session = service.create_session(device_id)
    return RemoteSessionOut(
        id=session.id,
        device_id=session.device_id,
        state=session.state,
        created_at=session.created_at,
    )


@router.get("/sessions", response_model=list[RemoteSessionOut])
def list_sessions(db: Session = Depends(get_db)) -> list[RemoteSessionOut]:
    service = RemoteSessionService(db)
    return [
        RemoteSessionOut(
            id=s.id, device_id=s.device_id, state=s.state, created_at=s.created_at
        )
        for s in service.list_sessions()
    ]


@router.delete("/sessions/{session_id}", response_model=StatusResponse)
def end_session(session_id: str, db: Session = Depends(get_db)) -> StatusResponse:
    service = RemoteSessionService(db)
    if not service.end_session(session_id):
        raise HTTPException(status_code=404, detail="session not found")
    return StatusResponse(detail="ended")
