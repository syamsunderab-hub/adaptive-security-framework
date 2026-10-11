import { NodeState, SecurityLevel } from "../types/node";
import { SystemStatus, DemoProgress } from "../types/security";
import { ThreatEvent, ThreatType } from "../types/threat";
import { SystemEvent } from "../types/event";

const API_BASE = "/api";

export async function fetchNodes(): Promise<NodeState[]> {
  const res = await fetch(`${API_BASE}/nodes`);
  if (!res.ok) throw new Error("Failed to fetch nodes");
  return res.json();
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/system/status`);
  if (!res.ok) throw new Error("Failed to fetch system status");
  return res.json();
}

export async function fetchEvents(limit = 50): Promise<SystemEvent[]> {
  const res = await fetch(`${API_BASE}/events?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch events");
  return res.json();
}

export async function fetchThreats(): Promise<ThreatEvent[]> {
  const res = await fetch(`${API_BASE}/threats`);
  if (!res.ok) throw new Error("Failed to fetch threats");
  return res.json();
}

export async function triggerAttack(nodeId: string, threatType: ThreatType): Promise<any> {
  const res = await fetch(`${API_BASE}/nodes/${nodeId}/attack`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ threat_type: threatType })
  });
  return res.json();
}

export async function failNode(nodeId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/nodes/${nodeId}/fail`, { method: "POST" });
  return res.json();
}

export async function recoverNode(nodeId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/nodes/${nodeId}/recover`, { method: "POST" });
  return res.json();
}

export async function setSecurityLevel(nodeId: string, securityLevel: SecurityLevel): Promise<any> {
  const res = await fetch(`${API_BASE}/nodes/${nodeId}/security-level`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ security_level: securityLevel })
  });
  return res.json();
}

export async function executeNodeAction(nodeId: string, action: string): Promise<any> {
  const res = await fetch(`${API_BASE}/nodes/${nodeId}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action })
  });
  return res.json();
}

export async function startSimulation(): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/start`, { method: "POST" });
  return res.json();
}

export async function stopSimulation(): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/stop`, { method: "POST" });
  return res.json();
}

export async function resetSimulation(): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/reset`, { method: "POST" });
  return res.json();
}

export async function triggerFullDemo(): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/demo`, { method: "POST" });
  return res.json();
}

export async function fetchSimStatus(): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/status`);
  return res.json();
}
