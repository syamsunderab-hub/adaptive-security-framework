from fastapi import APIRouter, Query
from typing import List, Dict, Any
from ..state.system_state import system_state

router = APIRouter(prefix="", tags=["Events & Threats"])

@router.get("/events")
async def get_events(limit: int = Query(default=50, ge=1, le=200)):
    return system_state.get_events(limit=limit)

@router.get("/threats")
async def get_threats():
    return system_state.get_threats()

@router.get("/adaptations")
async def get_adaptations():
    return system_state.get_adaptations()
