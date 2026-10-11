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
