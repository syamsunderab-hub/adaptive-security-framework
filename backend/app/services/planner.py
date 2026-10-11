from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..models.node import NodeState, SecurityLevel
from ..models.threat import ThreatType, ThreatSeverity
from ..models.security import AdaptationAction
from .security_manager import security_level_manager
from ..core.config import settings
import time

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
    observed_telemetry: Dict[str, Any] = {}
    baseline: Dict[str, Any] = {}
    risk_components: Dict[str, float] = {}
    threshold: Optional[float] = None

class Planner:
    def plan(
        self,
        node: NodeState,
        risk_score: float,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        recommended_action: str,
        observed_telemetry: Optional[Dict[str, Any]] = None,
        baseline: Optional[Dict[str, Any]] = None,
        risk_components: Optional[Dict[str, float]] = None,
    ) -> AdaptationPlan:
        # Determine target security level based on calculated risk score
        requested_level = security_level_manager.calculate_level_from_score(risk_score)
        target_level = requested_level
        # A single normal sample must not undo an active restriction. Escalations
        # remain immediate; relaxation requires consecutive clean observations and
        # a cooldown, both configurable in Settings.
        relaxing = requested_level.level_int > node.security_level.level_int
        clean_observations = int(node.metadata.get("normal_observations", 0))
        last_change = float(node.metadata.get("last_adaptation_at", 0.0))
        cooldown_active = (time.time() - last_change) < settings.ADAPTATION_COOLDOWN_SECONDS
        if relaxing and (
            threat_type != ThreatType.NORMAL or
            clean_observations < settings.DEESCALATION_CONSECUTIVE_OBSERVATIONS or
            cooldown_active
        ):
            target_level = node.security_level
        action, restrictions = security_level_manager.determine_action_for_level(target_level)

        # Upstream propagation logic:
        # If target level escalates beyond DEFCON 4 (i.e. DEFCON 3, 2, 1), notify parent fog/cloud
        should_propagate = (target_level.level_int < node.security_level.level_int) and (target_level.level_int <= 3)

        reason = (
            f"Risk score {risk_score} (severity: {severity.value}) requested {requested_level.value} "
            f"from {node.security_level.value}; selected {target_level.value}. {recommended_action}"
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
            severity=severity,
            observed_telemetry=observed_telemetry or {},
            baseline=baseline or {},
            risk_components=risk_components or {},
            threshold=risk_score
        )

planner_engine = Planner()
