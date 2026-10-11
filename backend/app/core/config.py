from pydantic import BaseModel
from typing import Dict, List, Optional

class DefconThresholds(BaseModel):
    DEFCON_5_MAX: float = 24.0   # 0 - 24: Normal
    DEFCON_4_MAX: float = 49.0   # 25 - 49: Elevated
    DEFCON_3_MAX: float = 69.0   # 50 - 69: Guarded
    DEFCON_2_MAX: float = 89.0   # 70 - 89: Moderate
    # 90 - 100: Maximum (DEFCON 1)

class NodeConfig(BaseModel):
    id: str
    name: str
    node_type: str  # CLOUD, FOG, EDGE
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    initial_cpu: float = 12.0
    initial_traffic: float = 120.0
    initial_connections: int = 45

class Settings(BaseModel):
    PROJECT_NAME: str = "Adaptive Security Framework"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    HEARTBEAT_INTERVAL_SECONDS: float = 2.0
    HEARTBEAT_TIMEOUT_SECONDS: float = 6.0
    RECOVERY_VALIDATION_SECONDS: float = 4.0
    DEESCALATION_CONSECUTIVE_OBSERVATIONS: int = 3
    ADAPTATION_COOLDOWN_SECONDS: float = 5.0
    DATABASE_PATH: str = "adaptive_security.db"
    
    DEFCON_THRESHOLDS: DefconThresholds = DefconThresholds()
    
    # Topology definition
    DEFAULT_NODES: List[NodeConfig] = [
        NodeConfig(
            id="CLOUD",
            name="Cloud Master Controller",
            node_type="CLOUD",
            parent_id=None,
            children_ids=["FOG-01", "FOG-02"],
            initial_cpu=18.5,
            initial_traffic=450.0,
            initial_connections=120
        ),
        NodeConfig(
            id="FOG-01",
            name="Fog Gateway Alpha",
            node_type="FOG",
            parent_id="CLOUD",
            children_ids=["EDGE-01", "EDGE-02"],
            initial_cpu=14.0,
            initial_traffic=210.0,
            initial_connections=65
        ),
        NodeConfig(
            id="FOG-02",
            name="Fog Gateway Beta",
            node_type="FOG",
            parent_id="CLOUD",
            children_ids=["EDGE-03", "EDGE-04"],
            initial_cpu=13.5,
            initial_traffic=195.0,
            initial_connections=60
        ),
        NodeConfig(
            id="EDGE-01",
            name="Edge Sensor Hub 1",
            node_type="EDGE",
            parent_id="FOG-01",
            children_ids=[],
            initial_cpu=8.5,
            initial_traffic=85.0,
            initial_connections=25
        ),
        NodeConfig(
            id="EDGE-02",
            name="Edge Telemetry Hub 2",
            node_type="EDGE",
            parent_id="FOG-01",
            children_ids=[],
            initial_cpu=9.0,
            initial_traffic=92.0,
            initial_connections=28
        ),
        NodeConfig(
            id="EDGE-03",
            name="Edge Actuator Hub 3",
            node_type="EDGE",
            parent_id="FOG-02",
            children_ids=[],
            initial_cpu=8.0,
            initial_traffic=80.0,
            initial_connections=22
        ),
        NodeConfig(
            id="EDGE-04",
            name="Edge Gateway Hub 4",
            node_type="EDGE",
            parent_id="FOG-02",
            children_ids=[],
            initial_cpu=9.5,
            initial_traffic=95.0,
            initial_connections=30
        ),
    ]

settings = Settings()
