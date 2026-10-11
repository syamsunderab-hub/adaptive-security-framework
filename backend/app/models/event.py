from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid

class SystemEventType(str, Enum):
    NODE_UPDATE = "node_update"
    SECURITY_LEVEL_CHANGED = "security_level_changed"
    THREAT_DETECTED = "threat_detected"
    HEARTBEAT_LOST = "heartbeat_lost"
    NODE_RECOVERED = "node_recovered"
    ADAPTATION_STARTED = "adaptation_started"
    ADAPTATION_COMPLETED = "adaptation_completed"
    MODE_CHANGED = "mode_changed"
    MAPEK_UPDATE = "mape_k_update"
    SIMULATION_STEP = "simulation_step"
    NODE_ISOLATED = "node_isolated"

class SystemEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:6].upper()}")
    timestamp: float = Field(default_factory=time.time)
    formatted_time: str = ""
    event_type: SystemEventType
    node_id: Optional[str] = None
    message: str
    severity: str = "INFO"  # INFO, WARNING, CRITICAL, SUCCESS
    details: Dict[str, Any] = {}

    def model_post_init(self, __context: Any) -> None:
        if not self.formatted_time:
            lt = time.localtime(self.timestamp)
            self.formatted_time = time.strftime("%H:%M:%S", lt)
