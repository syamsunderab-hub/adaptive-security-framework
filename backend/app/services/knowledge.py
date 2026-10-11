from typing import List, Dict, Any, Optional
import time
from ..models.event import SystemEvent
from ..models.threat import ThreatEvent
from ..models.security import AdaptationRecord
from ..models.node import SecurityLevel

class KnowledgeBase:
    def __init__(self):
        self.events_history: List[SystemEvent] = []
        self.threats_history: List[ThreatEvent] = []
        self.adaptation_history: List[AdaptationRecord] = []
        
        # Baselines per node type
        self.baselines: Dict[str, Dict[str, float]] = {
            "CLOUD": {
                "cpu": 18.0,
                "traffic": 450.0,
                "connections": 120.0,
                "failed_auths": 0.0
            },
            "FOG": {
                "cpu": 14.0,
                "traffic": 200.0,
                "connections": 60.0,
                "failed_auths": 0.0
            },
            "EDGE": {
                "cpu": 8.0,
                "traffic": 85.0,
                "connections": 25.0,
                "failed_auths": 0.0
            }
        }
        
        # Policy rules
        self.policies: Dict[SecurityLevel, Dict[str, Any]] = {
            SecurityLevel.DEFCON_5: {
                "name": "NORMAL",
                "description": "Standard monitoring, all traffic allowed, default logging",
                "rate_limit_pps": None,
                "isolated": False
            },
            SecurityLevel.DEFCON_4: {
                "name": "ELEVATED",
                "description": "Increased telemetry sampling, detailed debug logging",
                "rate_limit_pps": None,
                "isolated": False
            },
            SecurityLevel.DEFCON_3: {
                "name": "GUARDED",
                "description": "Flag suspicious sources, generate security event, enhanced inspection",
                "rate_limit_pps": 1500,
                "isolated": False
            },
            SecurityLevel.DEFCON_2: {
                "name": "MODERATE",
                "description": "Simulated rate limiting active, restrict suspicious traffic, high severity alert",
                "rate_limit_pps": 500,
                "isolated": False
            },
            SecurityLevel.DEFCON_1: {
                "name": "MAXIMUM",
                "description": "Simulated node isolation, block suspicious source, stop non-essential traffic",
                "rate_limit_pps": 50,
                "isolated": True
            }
        }

    def record_event(self, event: SystemEvent):
        self.events_history.insert(0, event)
        if len(self.events_history) > 500:
            self.events_history.pop()

    def record_threat(self, threat: ThreatEvent):
        self.threats_history.insert(0, threat)
        if len(self.threats_history) > 200:
            self.threats_history.pop()

    def record_adaptation(self, adaptation: AdaptationRecord):
        self.adaptation_history.insert(0, adaptation)
        if len(self.adaptation_history) > 200:
            self.adaptation_history.pop()

    def get_baseline(self, node_type: str) -> Dict[str, float]:
        return self.baselines.get(node_type, self.baselines["EDGE"])

knowledge_base = KnowledgeBase()
