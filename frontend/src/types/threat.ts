export type ThreatType = "NORMAL" | "ICMP_FLOOD" | "PORT_SCAN" | "ABNORMAL_CONNECTIONS" | "BRUTE_FORCE_AUTH";
export type ThreatSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface ThreatEvent {
  threat_id: string;
  node_id: string;
  threat_type: ThreatType;
  severity: ThreatSeverity;
  confidence: number;
  timestamp: number;
  description: string;
  recommended_action: string;
  metrics_snapshot?: Record<string, any>;
}
