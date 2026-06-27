"""Audio (STT/TTS) endpoints (Mocked for Phase 6)."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

router = APIRouter(prefix="/audio", tags=["audio"])


class SynthesizeRequest(BaseModel):
    text: str
    voice: str | None = None


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> JSONResponse:
    """Mock STT transcription."""
    return JSONResponse({"text": "Mock transcription"})


@router.post("/synthesize")
async def synthesize_audio(body: SynthesizeRequest) -> Response:
    """Mock TTS synthesis. Returns a 404 or empty audio since we have no real engine."""
    raise HTTPException(status_code=404, detail="TTS engine not configured (Phase 6 mock)")
