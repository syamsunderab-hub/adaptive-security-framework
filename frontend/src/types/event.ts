export interface SystemEvent {
  id: string;
  timestamp: number;
  formatted_time: string;
  event_type: string;
  node_id?: string;
  message: string;
  severity: "INFO" | "WARNING" | "CRITICAL" | "SUCCESS";
  details?: Record<string, any>;
}
