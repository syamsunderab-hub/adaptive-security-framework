import { useState, useEffect } from "react";
import { NodeState } from "../types/node";
import { SystemStatus, DemoProgress } from "../types/security";
import { SystemEvent } from "../types/event";
import { ThreatEvent } from "../types/threat";
import { wsClient } from "../services/websocket";
import { fetchNodes, fetchSystemStatus, fetchEvents, fetchThreats } from "../services/api";

export function useSystemState() {
  const [nodes, setNodes] = useState<Record<string, NodeState>>({});
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>("EDGE-02");
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [events, setEvents] = useState<SystemEvent[]>([]);
  const [threats, setThreats] = useState<ThreatEvent[]>([]);
  const [demoProgress, setDemoProgress] = useState<DemoProgress | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const [lastHeartbeatTick, setLastHeartbeatTick] = useState<number>(Date.now());

  // Initial load
  useEffect(() => {
    async function loadInitial() {
      try {
        const [loadedNodes, loadedStatus, loadedEvents, loadedThreats] = await Promise.all([
          fetchNodes(),
          fetchSystemStatus(),
          fetchEvents(30),
          fetchThreats()
        ]);
        const nodeMap: Record<string, NodeState> = {};
        loadedNodes.forEach((n) => { nodeMap[n.node_id] = n; });
        setNodes(nodeMap);
        setSystemStatus(loadedStatus);
        setEvents(loadedEvents);
        setThreats(loadedThreats);
      } catch (err) {
        console.error("Initial data load error:", err);
      }
    }
    loadInitial();
  }, []);

  // WebSocket subscriptions
  useEffect(() => {
    wsClient.connect();
    const unsubStatus = wsClient.onStatusChange(setConnected);

    const unsubInit = wsClient.subscribe("init_state", (data) => {
      if (data.nodes) setNodes(data.nodes);
      if (data.system_status) setSystemStatus(data.system_status);
      if (data.events) setEvents(data.events);
      if (data.threats) setThreats(data.threats);
    });

    const unsubSnapshot = wsClient.subscribe("nodes_snapshot", (nodesData) => {
      setNodes(nodesData);
      setLastHeartbeatTick(Date.now());
    });

    const unsubNodeUpdate = wsClient.subscribe("node_update", (node: NodeState) => {
      setNodes((prev) => ({ ...prev, [node.node_id]: node }));
    });

    const unsubSecChanged = wsClient.subscribe("security_level_changed", (data) => {
      if (data.event) {
        setEvents((prev) => [data.event, ...prev.slice(0, 49)]);
      }
    });

    const unsubThreat = wsClient.subscribe("threat_detected", (threat: ThreatEvent) => {
      setThreats((prev) => [threat, ...prev.slice(0, 29)]);
    });

    const unsubHeartbeatLost = wsClient.subscribe("heartbeat_lost", (data) => {
      if (data.event) {
        setEvents((prev) => [data.event, ...prev.slice(0, 49)]);
      }
      setNodes((prev) => {
        if (!prev[data.node_id]) return prev;
        return {
          ...prev,
          [data.node_id]: { ...prev[data.node_id], status: "OFFLINE", heartbeat_status: "TIMEOUT" }
        };
      });
    });

    const unsubNodeRecovered = wsClient.subscribe("node_recovered", (data) => {
      if (data.event) {
        setEvents((prev) => [data.event, ...prev.slice(0, 49)]);
      }
      setNodes((prev) => {
        if (!prev[data.node_id]) return prev;
        return {
          ...prev,
          [data.node_id]: { ...prev[data.node_id], status: "ONLINE", heartbeat_status: "HEALTHY" }
        };
      });
    });

    const unsubModeChanged = wsClient.subscribe("mode_changed", (data) => {
      if (data.event) {
        setEvents((prev) => [data.event, ...prev.slice(0, 49)]);
      }
      setSystemStatus((prev) => prev ? { ...prev, global_mode: data.new_mode } : null);
    });

    const unsubSystemStatus = wsClient.subscribe("system_status", (status: SystemStatus) => {
      setSystemStatus(status);
    });

    const unsubDemo = wsClient.subscribe("demo_progress", (progress: DemoProgress) => {
      setDemoProgress(progress);
      if (progress.current_step >= progress.total_steps || progress.current_step === 0) {
        setTimeout(() => setDemoProgress(null), 5000);
      }
    });

    const unsubSimEvt = wsClient.subscribe("simulation_event", (evt: SystemEvent) => {
      setEvents((prev) => [evt, ...prev.slice(0, 49)]);
    });

    const unsubReset = wsClient.subscribe("system_reset", (data) => {
      if (data.event) setEvents((prev) => [data.event, ...prev.slice(0, 49)]);
      if (data.nodes) setNodes(data.nodes);
    });

    return () => {
      unsubStatus();
      unsubInit();
      unsubSnapshot();
      unsubNodeUpdate();
      unsubSecChanged();
      unsubThreat();
      unsubHeartbeatLost();
      unsubNodeRecovered();
      unsubModeChanged();
      unsubSystemStatus();
      unsubDemo();
      unsubSimEvt();
      unsubReset();
    };
  }, []);

  const selectedNode = selectedNodeId && nodes[selectedNodeId] ? nodes[selectedNodeId] : null;

  return {
    nodes,
    selectedNodeId,
    setSelectedNodeId,
    selectedNode,
    systemStatus,
    events,
    threats,
    demoProgress,
    connected,
    lastHeartbeatTick
  };
}
