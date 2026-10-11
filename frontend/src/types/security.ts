import { SecurityLevel } from "./node";

export type AdaptationMode = "FULL_ADAPTATION" | "PARTIAL_ADAPTATION";

export interface AdaptationGroup {
  group_id: string;
  name: string;
  total_members: number;
  online_members: string[];
  offline_members: string[];
  is_degraded: boolean;
  most_restrictive_level: SecurityLevel;
}

export interface SystemStatus {
  system_name: string;
  global_mode: AdaptationMode;
  overall_threat_level: SecurityLevel;
  most_restrictive_level: SecurityLevel;
  online_nodes: number;
  offline_nodes: number;
  recovering_nodes: number;
  total_nodes: number;
  active_threats_count: number;
  avg_risk_score: number;
  last_update: number;
  isolated_nodes: string[];
  active_adaptation_groups: AdaptationGroup[];
}

export interface DemoProgress {
  current_step: number;
  total_steps: number;
  status_text: string;
}
