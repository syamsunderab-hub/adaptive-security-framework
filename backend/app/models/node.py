from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import time

class NodeType(str, Enum):
    CLOUD = "CLOUD"
    FOG = "FOG"
    EDGE = "EDGE"

class NodeStatus(str, Enum):
    ONLINE = "ONLINE"
    RECOVERING = "RECOVERING"
    OFFLINE = "OFFLINE"
    ISOLATED = "ISOLATED"

class SecurityLevel(str, Enum):
    DEFCON_5 = "DEFCON_5"  # Normal
    DEFCON_4 = "DEFCON_4"  # Elevated
    DEFCON_3 = "DEFCON_3"  # Guarded
    DEFCON_2 = "DEFCON_2"  # Moderate
    DEFCON_1 = "DEFCON_1"  # Maximum

    @property
    def level_int(self) -> int:
        return int(self.value.split("_")[1])

    @classmethod
    def from_int(cls, val: int) -> "SecurityLevel":
        return cls(f"DEFCON_{val}")

class MapeKStage(str, Enum):
    IDLE = "IDLE"
    MONITOR = "MONITOR"
    ANALYZE = "ANALYZE"
    PLAN = "PLAN"
    EXECUTE = "EXECUTE"

class NodeTelemetry(BaseModel):
    cpu_percent: float = Field(default=10.0, ge=0.0, le=100.0)
    network_traffic_pps: float = Field(default=100.0, ge=0.0)
    connection_count: int = Field(default=30, ge=0)
    failed_auth_count: int = Field(default=0, ge=0)
    packet_rate: float = Field(default=100.0, ge=0.0)
    timestamp: float = Field(default_factory=time.time)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_finite(cls, value: float) -> float:
        if not isinstance(value, (int, float)) or value != value or value in (float("inf"), float("-inf")):
            raise ValueError("timestamp must be finite")
        return value

class NodeState(BaseModel):
    node_id: str
    name: str
    node_type: NodeType
    status: NodeStatus = NodeStatus.ONLINE
    security_level: SecurityLevel = SecurityLevel.DEFCON_5
    threat_score: float = 5.0
    current_threat: str = "NORMAL"
    threat_details: Optional[str] = None
    cpu_usage: float = 10.0
    network_traffic: float = 100.0
    connections: int = 30
    failed_auths: int = 0
    heartbeat_status: str = "HEALTHY"
    last_heartbeat: float = Field(default_factory=time.time)
    mape_k_stage: MapeKStage = MapeKStage.IDLE
    last_adaptation: str = "INITIAL"
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    active_restrictions: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NodeUpdateReq(BaseModel):
    security_level: Optional[SecurityLevel] = None
    status: Optional[NodeStatus] = None
    threat_score: Optional[float] = None
