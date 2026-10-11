from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models.node import NodeState, SecurityLevel
from ..models.threat import ThreatType, ThreatSeverity
from ..state.system_state import system_state
from ..services.security_manager import security_level_manager
from ..services.planner import AdaptationPlan
from ..services.executor import executor_engine
from ..services.monitor import monitor_engine
from ..core.websocket_manager import websocket_manager

router = APIRouter(prefix="/nodes", tags=["Nodes"])

class AttackRequest(BaseModel):
    threat_type: ThreatType = ThreatType.ICMP_FLOOD

class SecurityLevelRequest(BaseModel):
    security_level: SecurityLevel

class NodeActionRequest(BaseModel):
    action: str  # "rate_limit", "isolate", "increase_monitoring", "reset"

@router.get("", response_model=List[NodeState])
async def get_all_nodes():
    return system_state.get_all_nodes()

@router.get("/{node_id}", response_model=NodeState)
async def get_node(node_id: str = Path(...)):
    node = system_state.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return node

@router.post("/{node_id}/fail")
async def fail_node(node_id: str = Path(...)):
    success = await system_state.simulation.fail_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Node {node_id} could not be failed")
    return {"status": "ok", "message": f"Node {node_id} failed, heartbeat terminated"}

@router.post("/{node_id}/recover")
async def recover_node(node_id: str = Path(...)):
    success = await system_state.simulation.recover_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Node {node_id} recovery failed")
    return {"status": "ok", "message": f"Node {node_id} recovery initiated"}

@router.post("/{node_id}/attack")
async def attack_node(req: AttackRequest, node_id: str = Path(...)):
    success = await system_state.simulation.trigger_attack(node_id, req.threat_type)
    if not success:
        raise HTTPException(status_code=404, detail=f"Attack could not be applied to node {node_id}")
    return {"status": "ok", "message": f"Injected {req.threat_type.value} on {node_id}"}

@router.post("/{node_id}/security-level")
async def set_security_level(req: SecurityLevelRequest, node_id: str = Path(...)):
    node = system_state.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    action, restrictions = security_level_manager.determine_action_for_level(req.security_level)
    plan = AdaptationPlan(
        node_id=node.node_id,
        previous_level=node.security_level,
        target_level=req.security_level,
        action=action,
        restrictions=restrictions,
        should_propagate_upstream=True,
        upstream_target=node.parent_id,
        reason=f"Manual operator override to {req.security_level.value}",
        threat_type=ThreatType.NORMAL,
        severity=ThreatSeverity.MEDIUM
    )
    await executor_engine.execute_plan(node, plan, system_state.controller.global_mode)
    await websocket_manager.broadcast("node_update", node.model_dump())
    return {"status": "ok", "node": node}

@router.post("/{node_id}/action")
async def perform_node_action(req: NodeActionRequest, node_id: str = Path(...)):
    node = system_state.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

    act = req.action.lower()
    if act in ("rate_limit", "rate-limit"):
        target_level = SecurityLevel.DEFCON_2
        sev = ThreatSeverity.HIGH
    elif act in ("isolate", "isolate_node"):
        target_level = SecurityLevel.DEFCON_1
        sev = ThreatSeverity.CRITICAL
    elif act in ("increase_monitoring", "increase-monitoring"):
        target_level = SecurityLevel.DEFCON_4
        sev = ThreatSeverity.LOW
    elif act in ("reset", "normal"):
        system_state.simulation.stop_attack(node_id)
        target_level = SecurityLevel.DEFCON_5
        sev = ThreatSeverity.LOW
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {req.action}")

    action_enum, restrictions = security_level_manager.determine_action_for_level(target_level)
    plan = AdaptationPlan(
        node_id=node.node_id,
        previous_level=node.security_level,
        target_level=target_level,
        action=action_enum,
        restrictions=restrictions,
        should_propagate_upstream=(target_level.level_int <= 3),
        upstream_target=node.parent_id,
        reason=f"Operator requested action: {req.action}",
        threat_type=ThreatType.NORMAL,
        severity=sev
    )
    await executor_engine.execute_plan(node, plan, system_state.controller.global_mode)
    await websocket_manager.broadcast("node_update", node.model_dump())
    return {"status": "ok", "action_applied": req.action, "node": node}

@router.get("/mape-k/{node_id}")
async def get_node_mape_k(node_id: str = Path(...)):
    node = system_state.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    baseline = system_state.knowledge.get_baseline(node.node_type.value)
    return {
        "node_id": node.node_id,
        "mape_k_stage": node.mape_k_stage.value,
        "current_telemetry": {
            "cpu_percent": node.cpu_usage,
            "network_traffic_pps": node.network_traffic,
            "connection_count": node.connections,
            "failed_auth_count": node.failed_auths
        },
        "baseline": baseline,
        "threat_score": node.threat_score,
        "current_threat": node.current_threat,
        "security_level": node.security_level.value,
        "active_restrictions": node.active_restrictions,
        "last_adaptation": node.last_adaptation
    }
