from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid

class ThreatType(str, Enum):
    NORMAL = "NORMAL"
    ICMP_FLOOD = "ICMP_FLOOD"
    PORT_SCAN = "PORT_SCAN"
    ABNORMAL_CONNECTIONS = "ABNORMAL_CONNECTIONS"
    BRUTE_FORCE_AUTH = "BRUTE_FORCE_AUTH"

class ThreatSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ThreatEvent(BaseModel):
    threat_id: str = Field(default_factory=lambda: f"THR-{uuid.uuid4().hex[:6].upper()}")
    node_id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float = 0.95
    timestamp: float = Field(default_factory=time.time)
    description: str
    recommended_action: str
    metrics_snapshot: Dict[str, Any] = {}
