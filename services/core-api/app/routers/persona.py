"""Persona endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.persona import PersonaModeUpdate, PersonaOut
from app.services.persona.service import persona_service

router = APIRouter(prefix="/persona", tags=["persona"])


def _persona_out() -> PersonaOut:
    cfg = persona_service.get_persona()
    return PersonaOut(
        name=cfg.name,
        tone=cfg.tone,
        relationship_mode=cfg.relationship_mode,
        verbosity=cfg.verbosity,
        humor_level=cfg.humor_level,
        operator_mode_style=cfg.operator_mode_style,
        voice_profile=cfg.voice_profile,
        presence_theme=cfg.presence_theme,
        active_mode=persona_service.active_mode,
        system_prompt=persona_service.active_prompt(),
    )


@router.get("", response_model=PersonaOut)
def get_persona() -> PersonaOut:
    return _persona_out()


@router.get("/modes", response_model=list[str])
def list_modes() -> list[str]:
    return persona_service.list_modes()


@router.post("/mode", response_model=PersonaOut)
def set_mode(body: PersonaModeUpdate) -> PersonaOut:
    try:
        persona_service.set_mode(body.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _persona_out()
