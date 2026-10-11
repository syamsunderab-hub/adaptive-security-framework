from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from ..models.node import NodeTelemetry
from ..models.threat import ThreatType, ThreatSeverity

class ThreatAnalyzer(ABC):
    @abstractmethod
    def analyze(self, telemetry: NodeTelemetry, baseline: Dict[str, float]) -> Tuple[float, ThreatType, ThreatSeverity, float, str, str]:
        """
        Analyzes telemetry against baselines.
        Returns: (risk_score, threat_type, severity, confidence, description, recommended_action)
        """
        pass

class RuleBasedAnalyzer(ThreatAnalyzer):
    def analyze(self, telemetry: NodeTelemetry, baseline: Dict[str, float]) -> Tuple[float, ThreatType, ThreatSeverity, float, str, str]:
        base_traffic = max(1.0, baseline.get("traffic", 100.0))
        base_conn = max(1.0, baseline.get("connections", 30.0))
        base_cpu = max(1.0, baseline.get("cpu", 10.0))

        # Calculate anomaly ratios
        traffic_ratio = max(0.0, (telemetry.network_traffic_pps - base_traffic) / base_traffic)
        conn_ratio = max(0.0, (telemetry.connection_count - base_conn) / base_conn)
        cpu_ratio = max(0.0, (telemetry.cpu_percent - base_cpu) / base_cpu)
        auth_ratio = min(1.0, telemetry.failed_auth_count / 10.0)

        # Indicator scores (0 - 100 each)
        traffic_score = min(100.0, (traffic_ratio / 6.0) * 100.0)
        conn_score = min(100.0, (conn_ratio / 4.0) * 100.0)
        auth_score = min(100.0, auth_ratio * 100.0)
        cpu_score = min(100.0, (cpu_ratio / 4.0) * 100.0)
        
        # Other indicators (e.g. combined turbulence)
        turbulence = min(100.0, (traffic_score * 0.5 + conn_score * 0.5))

        # Modular weighted risk score
        # 30% traffic, 20% connection, 15% authentication, 10% CPU, 25% other
        weighted_score = (
            0.30 * traffic_score +
            0.20 * conn_score +
            0.15 * auth_score +
            0.10 * cpu_score +
            0.25 * turbulence
        )
        risk_score = round(min(100.0, max(0.0, weighted_score)), 1)

        # Threat classification
        threat_type = ThreatType.NORMAL
        confidence = 0.90
        description = "System metrics within normal operational variance."
        recommended_action = "Maintain baseline monitoring."

        if telemetry.failed_auth_count >= 5 or auth_score >= 50.0:
            threat_type = ThreatType.BRUTE_FORCE_AUTH
            confidence = 0.94
            description = f"High rate of failed authentications detected ({telemetry.failed_auth_count} attempts)."
            recommended_action = "Enforce rate limiting and lockout suspicious credentials."
        elif traffic_ratio >= 3.5 or telemetry.network_traffic_pps >= 3000.0:
            threat_type = ThreatType.ICMP_FLOOD
            confidence = 0.93
            description = f"Massive packet surge detected ({telemetry.network_traffic_pps:.0f} pps, {traffic_ratio:.1f}x baseline)."
            recommended_action = "Simulate bandwidth throttling and upstream ingress filtering."
        elif conn_ratio >= 3.0 or telemetry.connection_count >= 400:
            threat_type = ThreatType.PORT_SCAN
            confidence = 0.89
            description = f"Rapid port scanning pattern detected ({telemetry.connection_count} active sockets)."
            recommended_action = "Flag source subnet and apply port knocking restriction."
        elif conn_ratio >= 1.5:
            threat_type = ThreatType.ABNORMAL_CONNECTIONS
            confidence = 0.85
            description = f"Elevated connection rate exceeding normal variance ({telemetry.connection_count} conns)."
            recommended_action = "Increase telemetry resolution and monitor session duration."

        # Severity
        if risk_score >= 90.0:
            severity = ThreatSeverity.CRITICAL
        elif risk_score >= 70.0:
            severity = ThreatSeverity.HIGH
        elif risk_score >= 50.0:
            severity = ThreatSeverity.MEDIUM
        else:
            severity = ThreatSeverity.LOW

        return risk_score, threat_type, severity, confidence, description, recommended_action

analyzer_engine = RuleBasedAnalyzer()
