from fastapi import APIRouter
from ..models.security import SystemStatusResponse
from ..state.system_state import system_state
from ..core.config import settings

router = APIRouter(prefix="", tags=["Security System"])

@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    return system_state.get_status()

@router.get("/security/policies")
async def get_security_policies():
    return {
        "thresholds": settings.DEFCON_THRESHOLDS.model_dump(),
        "policies": {
            lvl.value: pol for lvl, pol in system_state.knowledge.policies.items()
        }
    }

@router.get("/security/groups")
async def get_security_groups():
    return system_state.controller.get_system_status().active_adaptation_groups
