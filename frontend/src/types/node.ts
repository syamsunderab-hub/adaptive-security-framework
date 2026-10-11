export type NodeType = "CLOUD" | "FOG" | "EDGE";
export type NodeStatus = "ONLINE" | "RECOVERING" | "OFFLINE" | "ISOLATED";
export type SecurityLevel = "DEFCON_5" | "DEFCON_4" | "DEFCON_3" | "DEFCON_2" | "DEFCON_1";
export type MapeKStage = "IDLE" | "MONITOR" | "ANALYZE" | "PLAN" | "EXECUTE";

export interface NodeState {
  node_id: string;
  name: string;
  node_type: NodeType;
  status: NodeStatus;
  security_level: SecurityLevel;
  threat_score: number;
  current_threat: string;
  threat_details?: string;
  cpu_usage: number;
  network_traffic: number;
  connections: number;
  failed_auths: number;
  heartbeat_status: string;
  last_heartbeat: number;
  mape_k_stage: MapeKStage;
  last_adaptation: string;
  parent_id?: string;
  children_ids: string[];
  active_restrictions: string[];
}
