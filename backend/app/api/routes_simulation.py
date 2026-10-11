from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..models.threat import ThreatType
from ..state.system_state import system_state

router = APIRouter(prefix="/simulation", tags=["Simulation"])

class GlobalAttackRequest(BaseModel):
    node_id: str = "EDGE-02"
    threat_type: ThreatType = ThreatType.ICMP_FLOOD

@router.post("/start")
async def start_sim():
    system_state.simulation.start_simulation()
    return {"status": "ok", "is_running": system_state.simulation.is_running}

@router.post("/stop")
async def stop_sim():
    system_state.simulation.stop_simulation()
    return {"status": "ok", "is_running": system_state.simulation.is_running}

@router.post("/reset")
async def reset_sim():
    await system_state.simulation.reset_system()
    return {"status": "ok", "message": "System state reset to nominal baseline"}

@router.post("/attack")
async def trigger_sim_attack(req: GlobalAttackRequest):
    success = await system_state.simulation.trigger_attack(req.node_id, req.threat_type)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to inject attack on {req.node_id}")
    return {"status": "ok", "message": f"Injected {req.threat_type.value} on {req.node_id}"}

@router.post("/demo")
async def trigger_full_demo():
    if system_state.simulation.demo_in_progress:
        return {"status": "busy", "message": "Demo already running"}
    started = system_state.simulation.run_full_demo()
    return {"status": "ok", "demo_in_progress": started, "message": "11-step Adaptive Security Demo initiated"}

@router.get("/status")
async def get_sim_status():
    return {
        "is_running": system_state.simulation.is_running,
        "demo_in_progress": system_state.simulation.demo_in_progress,
        "demo_current_step": system_state.simulation.demo_current_step,
        "demo_total_steps": system_state.simulation.demo_total_steps,
        "demo_status_text": system_state.simulation.demo_status_text,
        "active_attacks": system_state.simulation.active_attacks
    }
