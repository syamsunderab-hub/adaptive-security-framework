from typing import Tuple, List
from ..models.node import SecurityLevel
from ..models.security import AdaptationAction
from ..core.config import settings

class SecurityLevelManager:
    def __init__(self):
        self.thresholds = settings.DEFCON_THRESHOLDS

    def calculate_level_from_score(self, risk_score: float) -> SecurityLevel:
        if risk_score <= self.thresholds.DEFCON_5_MAX:
            return SecurityLevel.DEFCON_5
        elif risk_score <= self.thresholds.DEFCON_4_MAX:
            return SecurityLevel.DEFCON_4
        elif risk_score <= self.thresholds.DEFCON_3_MAX:
            return SecurityLevel.DEFCON_3
        elif risk_score <= self.thresholds.DEFCON_2_MAX:
            return SecurityLevel.DEFCON_2
        else:
            return SecurityLevel.DEFCON_1

    def determine_action_for_level(self, level: SecurityLevel) -> Tuple[AdaptationAction, List[str]]:
        if level == SecurityLevel.DEFCON_5:
            return AdaptationAction.NORMAL_MONITORING, [
                "Standard monitoring profile active",
                "Ingress/egress filtering: Standard",
                "Logging verbosity: INFO"
            ]
        elif level == SecurityLevel.DEFCON_4:
            return AdaptationAction.INCREASE_LOGGING, [
                "Telemetry polling interval shortened to 1s",
                "Deep packet inspection logging enabled",
                "Logging verbosity: DEBUG"
            ]
        elif level == SecurityLevel.DEFCON_3:
            return AdaptationAction.FLAG_SUSPICIOUS, [
                "Suspicious source subnets flagged",
                "TCP SYN cookie challenge enforced",
                "Rate limit threshold: 1,500 pps",
                "Logging verbosity: DETAILED"
            ]
        elif level == SecurityLevel.DEFCON_2:
            return AdaptationAction.RATE_LIMIT, [
                "Aggressive traffic shaping: 500 pps ceiling",
                "Port scan source IPs dropped",
                "Critical alert broadcasted to Fog/Cloud controllers",
                "Non-essential background services paused"
            ]
        elif level == SecurityLevel.DEFCON_1:
            return AdaptationAction.ISOLATE_NODE, [
                "Simulated node isolation engaged",
                "Control-plane traffic only (Heartbeats + Auth)",
                "Host packet ingress blocked",
                "Failover redirection dispatched to peer nodes"
            ]
        return AdaptationAction.NORMAL_MONITORING, []

    @staticmethod
    def get_most_restrictive(levels: List[SecurityLevel]) -> SecurityLevel:
        if not levels:
            return SecurityLevel.DEFCON_5
        # DEFCON 1 is most restrictive (lowest integer)
        min_level_int = min(lvl.level_int for lvl in levels)
        return SecurityLevel.from_int(min_level_int)

security_level_manager = SecurityLevelManager()
