from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..models.node import NodeState, SecurityLevel
from ..models.threat import ThreatType, ThreatSeverity
from ..models.security import AdaptationAction
from .security_manager import security_level_manager

class AdaptationPlan(BaseModel):
    node_id: str
    previous_level: SecurityLevel
    target_level: SecurityLevel
    action: AdaptationAction
    restrictions: List[str]
    should_propagate_upstream: bool
    upstream_target: Optional[str] = None
    reason: str
    threat_type: ThreatType
    severity: ThreatSeverity

class Planner:
    def plan(
        self,
        node: NodeState,
        risk_score: float,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        recommended_action: str
    ) -> AdaptationPlan:
        # Determine target security level based on calculated risk score
        target_level = security_level_manager.calculate_level_from_score(risk_score)
        action, restrictions = security_level_manager.determine_action_for_level(target_level)

        # Upstream propagation logic:
        # If target level escalates beyond DEFCON 4 (i.e. DEFCON 3, 2, 1), notify parent fog/cloud
        should_propagate = (target_level.level_int < node.security_level.level_int) and (target_level.level_int <= 3)

        reason = (
            f"Risk score {risk_score} (severity: {severity.value}) triggered transition from "
            f"{node.security_level.value} to {target_level.value}. {recommended_action}"
        )

        return AdaptationPlan(
            node_id=node.node_id,
            previous_level=node.security_level,
            target_level=target_level,
            action=action,
            restrictions=restrictions,
            should_propagate_upstream=should_propagate,
            upstream_target=node.parent_id,
            reason=reason,
            threat_type=threat_type,
            severity=severity
        )

planner_engine = Planner()
