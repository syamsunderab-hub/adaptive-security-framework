from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import math
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
    def explain(self, telemetry: NodeTelemetry, baseline: Dict[str, float]) -> Dict[str, Any]:
        """Return deterministic, auditable analysis evidence for one telemetry sample."""
        for name, value in {
            "cpu_percent": telemetry.cpu_percent,
            "network_traffic_pps": telemetry.network_traffic_pps,
            "connection_count": telemetry.connection_count,
            "failed_auth_count": telemetry.failed_auth_count,
        }.items():
            if not math.isfinite(float(value)) or float(value) < 0:
                raise ValueError(f"{name} must be a finite non-negative value")
        for name in ("traffic", "connections", "cpu"):
            value = float(baseline.get(name, 0.0))
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"baseline {name} must be finite and greater than zero")

        base_traffic = float(baseline["traffic"])
        base_conn = float(baseline["connections"])
        base_cpu = float(baseline["cpu"])
        traffic_ratio = max(0.0, (telemetry.network_traffic_pps - base_traffic) / base_traffic)
        conn_ratio = max(0.0, (telemetry.connection_count - base_conn) / base_conn)
        cpu_ratio = max(0.0, (telemetry.cpu_percent - base_cpu) / base_cpu)
        auth_ratio = min(1.0, telemetry.failed_auth_count / 10.0)
        traffic_score = min(100.0, (traffic_ratio / 6.0) * 100.0)
        conn_score = min(100.0, (conn_ratio / 4.0) * 100.0)
        auth_score = min(100.0, auth_ratio * 100.0)
        cpu_score = min(100.0, (cpu_ratio / 4.0) * 100.0)
        turbulence = min(100.0, (traffic_score * 0.5 + conn_score * 0.5))
        weighted_score = (
            0.30 * traffic_score + 0.20 * conn_score + 0.15 * auth_score +
            0.10 * cpu_score + 0.25 * turbulence
        )
        return {
            "risk_score": round(min(100.0, max(0.0, weighted_score)), 1),
            "components": {
                "traffic": round(traffic_score, 2),
                "connections": round(conn_score, 2),
                "authentication": round(auth_score, 2),
                "cpu": round(cpu_score, 2),
                "turbulence": round(turbulence, 2),
            },
            "ratios": {"traffic": round(traffic_ratio, 4), "connections": round(conn_ratio, 4), "cpu": round(cpu_ratio, 4)},
            "weights": {"traffic": 0.30, "connections": 0.20, "authentication": 0.15, "cpu": 0.10, "turbulence": 0.25},
        }

    def analyze(self, telemetry: NodeTelemetry, baseline: Dict[str, float]) -> Tuple[float, ThreatType, ThreatSeverity, float, str, str]:
        evidence = self.explain(telemetry, baseline)
        risk_score = evidence["risk_score"]
        traffic_ratio = evidence["ratios"]["traffic"]
        conn_ratio = evidence["ratios"]["connections"]
        auth_score = evidence["components"]["authentication"]

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
