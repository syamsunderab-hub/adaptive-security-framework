from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid
from .node import SecurityLevel

class AdaptationMode(str, Enum):
    FULL_ADAPTATION = "FULL_ADAPTATION"
    PARTIAL_ADAPTATION = "PARTIAL_ADAPTATION"

class AdaptationAction(str, Enum):
    NORMAL_MONITORING = "NORMAL_MONITORING"
    INCREASE_LOGGING = "INCREASE_LOGGING"
    FLAG_SUSPICIOUS = "FLAG_SUSPICIOUS"
    RATE_LIMIT = "RATE_LIMIT"
    ISOLATE_NODE = "ISOLATE_NODE"
    RESTORE_NORMAL = "RESTORE_NORMAL"

class EnforcementMode(str, Enum):
    SIMULATED = "SIMULATED"
    ENFORCED = "ENFORCED"
    UNSUPPORTED = "UNSUPPORTED"

class ExecutionStatus(str, Enum):
    SIMULATED_SUCCESS = "SIMULATED_SUCCESS"
    ENFORCED_SUCCESS = "ENFORCED_SUCCESS"
    FAILED = "FAILED"
    UNSUPPORTED = "UNSUPPORTED"

class AdaptationRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"ADAPT-{uuid.uuid4().hex[:6].upper()}")
    timestamp: float = Field(default_factory=time.time)
    node_id: str
    previous_level: SecurityLevel
    new_level: SecurityLevel
    action_taken: AdaptationAction
    trigger_threat: str
    adaptation_mode: AdaptationMode
    affected_nodes: List[str] = []
    details: str = ""
    controller_id: str = "GLOBAL-CONTROLLER"
    observed_telemetry: Dict[str, Any] = {}
    baseline: Dict[str, Any] = {}
    risk_components: Dict[str, float] = {}
    risk_score: Optional[float] = None
    threshold: Optional[float] = None
    enforcement_mode: EnforcementMode = EnforcementMode.SIMULATED
    execution_status: ExecutionStatus = ExecutionStatus.SIMULATED_SUCCESS
    verification_result: str = "simulated state verified"
    execution_error: Optional[str] = None
    local_latency_ms: Optional[float] = None
    global_latency_ms: Optional[float] = None
    recovery_outcome: Optional[str] = None

class SystemStatusResponse(BaseModel):
    system_name: str
    global_mode: AdaptationMode
    overall_threat_level: SecurityLevel
    most_restrictive_level: SecurityLevel
    online_nodes: int
    offline_nodes: int
    recovering_nodes: int
    total_nodes: int
    active_threats_count: int
    avg_risk_score: float
    last_update: float = Field(default_factory=time.time)
    isolated_nodes: List[str] = []
    active_adaptation_groups: List[Dict[str, Any]] = []
