import React, { useState } from "react";
import {
  Cpu,
  Activity,
  Network,
  Shield,
  ShieldAlert,
  Radio,
  Flame,
  Power,
  RotateCcw,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Lock,
  Eye,
  Server
} from "lucide-react";
import { NodeState } from "../../types/node";
import { SecurityLevelBadge } from "../SecurityLevel/SecurityLevelBadge";
import {
  executeNodeAction,
  failNode,
  recoverNode,
  triggerAttack
} from "../../services/api";

interface Props {
  node: NodeState | null;
}

export const NodeDetails: React.FC<Props> = ({ node }) => {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  if (!node) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center text-slate-500">
        <Server className="h-10 w-10 text-slate-700 mb-2" />
        <p className="text-sm">Select any node in the topology to inspect security metrics and telemetry.</p>
      </div>
    );
  }

  const handleAction = async (action: string) => {
    setLoadingAction(action);
    try {
      if (action === "fail") {
        await failNode(node.node_id);
      } else if (action === "recover") {
        await recoverNode(node.node_id);
      } else {
        await executeNodeAction(node.node_id, action);
      }
    } catch (e) {
      console.error("Action error:", e);
    } finally {
      setLoadingAction(null);
    }
  };

  const isOnline = node.status === "ONLINE";
  const isRecovering = node.status === "RECOVERING";

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-slate-900/90 p-4 backdrop-blur-md">
      {/* Node Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold tracking-wide text-slate-100">{node.node_id}</h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {node.node_type}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">{node.name}</p>
        </div>
        <SecurityLevelBadge level={node.security_level} size="md" />
      </div>

      {/* Status & Heartbeat */}
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div className="rounded-lg bg-slate-950/70 p-2.5 border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Node Status</div>
          <div className="mt-1 flex items-center gap-1.5 font-bold">
            <span className={`h-2 w-2 rounded-full ${
              !isOnline ? "bg-red-500" : isRecovering ? "bg-amber-400 animate-pulse" : "bg-emerald-400 animate-pulse"
            }`} />
            <span className={!isOnline ? "text-red-400" : isRecovering ? "text-amber-400" : "text-emerald-400"}>
              {node.status}
            </span>
          </div>
        </div>

        <div className="rounded-lg bg-slate-950/70 p-2.5 border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Heartbeat</div>
          <div className="mt-1 font-mono font-bold text-slate-200">
            {node.heartbeat_status}
          </div>
        </div>
      </div>

      {/* Threat & Risk Card */}
      <div className="mt-3 rounded-lg bg-slate-950/70 p-3 border border-slate-800">
        <div className="flex items-center justify-between">
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Threat Assessment</div>
          <div className="text-xs font-mono font-bold text-slate-200">
            Risk: <span className={node.threat_score >= 70 ? "text-red-400" : node.threat_score >= 40 ? "text-amber-400" : "text-emerald-400"}>
              {node.threat_score} / 100
            </span>
          </div>
        </div>

        {/* Risk meter bar */}
        <div className="mt-2 h-2 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              node.threat_score >= 70 ? "bg-red-500" : node.threat_score >= 40 ? "bg-amber-500" : "bg-emerald-500"
            }`}
            style={{ width: `${Math.min(100, Math.max(5, node.threat_score))}%` }}
          />
        </div>

        <div className="mt-2.5 flex items-center justify-between text-xs">
          <span className="text-slate-400">Current Threat:</span>
          <span className={`font-semibold ${node.current_threat !== "NORMAL" ? "text-red-400" : "text-slate-200"}`}>
            {node.current_threat}
          </span>
        </div>

        {node.threat_details && (
          <p className="mt-1 text-[11px] text-slate-400 italic bg-slate-900/60 p-1.5 rounded border border-slate-800/80">
            "{node.threat_details}"
          </p>
        )}
      </div>

      {/* Live Telemetry Card */}
      <div className="mt-3 rounded-lg bg-slate-950/70 p-3 border border-slate-800">
        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Live Telemetry</div>
        <div className="space-y-2 text-xs">
          <div>
            <div className="flex justify-between text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><Cpu className="h-3.5 w-3.5 text-slate-500" /> CPU Usage</span>
              <span className="font-mono font-bold text-slate-200">{node.cpu_usage.toFixed(1)}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${Math.min(100, node.cpu_usage)}%` }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-slate-300 pt-1 border-t border-slate-800/60">
            <span className="flex items-center gap-1.5 text-slate-400"><Activity className="h-3.5 w-3.5 text-slate-500" /> Network Traffic</span>
            <span className="font-mono font-bold text-slate-100">{Math.round(node.network_traffic).toLocaleString()} pps</span>
          </div>

          <div className="flex items-center justify-between text-slate-300 pt-1 border-t border-slate-800/60">
            <span className="flex items-center gap-1.5 text-slate-400"><Network className="h-3.5 w-3.5 text-slate-500" /> Connections</span>
            <span className="font-mono font-bold text-slate-100">{node.connections.toLocaleString()}</span>
          </div>

          <div className="flex items-center justify-between text-slate-300 pt-1 border-t border-slate-800/60">
            <span className="flex items-center gap-1.5 text-slate-400"><ShieldAlert className="h-3.5 w-3.5 text-slate-500" /> Failed Auths</span>
            <span className={`font-mono font-bold ${node.failed_auths > 0 ? "text-amber-400" : "text-slate-100"}`}>{node.failed_auths}</span>
          </div>
        </div>
      </div>

      {/* MAPE-K & Adaptation Metadata */}
      <div className="mt-3 rounded-lg bg-slate-950/70 p-3 border border-slate-800 text-xs">
        <div className="flex items-center justify-between">
          <span className="text-slate-500 text-[10px] uppercase">MAPE-K State</span>
          <span className="font-mono font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/50">
            {node.mape_k_stage}
          </span>
        </div>
        <div className="mt-2 flex items-center justify-between text-slate-400">
          <span>Last Adaptation:</span>
          <span className="font-mono text-slate-200">{node.last_adaptation}</span>
        </div>
      </div>

      {/* Active Restrictions */}
      <div className="mt-3 rounded-lg bg-slate-950/70 p-3 border border-slate-800 text-xs">
        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5">Active Security Controls</div>
        <ul className="space-y-1">
          {node.active_restrictions.map((res, i) => (
            <li key={i} className="flex items-start gap-1.5 text-[11px] text-slate-300">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span>{res}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Operator Actions Deck */}
      <div className="mt-4 pt-3 border-t border-slate-800 space-y-2">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Security Controls & Interventions</div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <button
            onClick={() => handleAction("increase_monitoring")}
            disabled={!isOnline || loadingAction !== null}
            className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-950/60 hover:bg-blue-900/60 text-blue-300 border border-blue-700/50 disabled:opacity-40 transition-colors"
          >
            <Eye className="h-3.5 w-3.5" />
            <span>Increase Mon.</span>
          </button>

          <button
            onClick={() => handleAction("rate_limit")}
            disabled={!isOnline || loadingAction !== null}
            className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-amber-950/60 hover:bg-amber-900/60 text-amber-300 border border-amber-700/50 disabled:opacity-40 transition-colors"
          >
            <Sliders className="h-3.5 w-3.5" />
            <span>Rate Limit</span>
          </button>

          <button
            onClick={() => handleAction("isolate")}
            disabled={!isOnline || loadingAction !== null}
            className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-red-950/60 hover:bg-red-900/60 text-red-300 border border-red-700/50 disabled:opacity-40 transition-colors"
          >
            <Lock className="h-3.5 w-3.5" />
            <span>Isolate Node</span>
          </button>

          <button
            onClick={() => handleAction("reset")}
            disabled={!isOnline || loadingAction !== null}
            className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-700/50 disabled:opacity-40 transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset Normal</span>
          </button>
        </div>

        {/* Node Failure / Recovery Toggle */}
        <div className="pt-2 flex gap-2">
          {isOnline ? (
            <button
              onClick={() => handleAction("fail")}
              disabled={loadingAction !== null}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-red-950 hover:bg-red-900 text-red-200 border border-red-600 font-bold text-xs shadow-md transition-colors"
            >
              <Power className="h-3.5 w-3.5" />
              <span>Simulate Node Failure</span>
            </button>
          ) : (
            <button
              onClick={() => handleAction("recover")}
              disabled={loadingAction !== null || isRecovering}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-950 hover:bg-emerald-900 text-emerald-200 border border-emerald-500 font-bold text-xs shadow-md transition-colors animate-pulse"
            >
              <Power className="h-3.5 w-3.5" />
              <span>{isRecovering ? "Recovering..." : "Recover Node"}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
