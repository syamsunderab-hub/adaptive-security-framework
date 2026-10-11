import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Cpu, Activity, ShieldAlert, Radio } from "lucide-react";
import { NodeState } from "../../types/node";
import { SecurityLevelBadge } from "../SecurityLevel/SecurityLevelBadge";

interface EdgeNodeData {
  node: NodeState;
  isSelected?: boolean;
}

export const EdgeNode: React.FC<{ data: EdgeNodeData }> = ({ data }) => {
  const { node, isSelected } = data;
  const isOnline = node.status === "ONLINE";
  const isRecovering = node.status === "RECOVERING";
  const isAttacked = node.current_threat !== "NORMAL" && isOnline;

  const borderColor = !isOnline
    ? "border-red-900/50 bg-slate-900/50 opacity-60 grayscale"
    : isAttacked
    ? "border-red-500 bg-gradient-to-b from-slate-900 via-red-950/40 to-slate-900 shadow-2xl shadow-red-950/80 ring-2 ring-red-500/60 animate-pulse"
    : isSelected
    ? "border-blue-400 bg-slate-900 shadow-xl shadow-blue-950/60 ring-2 ring-blue-400/60"
    : "border-slate-800 bg-slate-900/95 hover:border-slate-600 shadow-lg";

  return (
    <div className={`relative w-[300px] rounded-2xl border p-3 backdrop-blur-md transition-all duration-200 cursor-pointer ${borderColor}`}>
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3.5 !h-3.5 !bg-blue-400 !border-2 !border-slate-950 shadow-md shadow-blue-500/50"
      />

      {/* Header */}
      <div className="flex items-center justify-between gap-2 border-b border-slate-800/90 pb-2">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-inner">
            <Radio className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-black tracking-wide text-slate-100">{node.node_id}</span>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/30 font-semibold">
                EDGE
              </span>
            </div>
            <div className="text-[10px] text-slate-400 font-semibold tracking-wide truncate max-w-[130px]">{node.name}</div>
          </div>
        </div>
        <SecurityLevelBadge level={node.security_level} size="sm" />
      </div>

      {/* Status & Risk Banner */}
      <div className="mt-2 flex items-center justify-between rounded-xl bg-slate-950/70 px-2.5 py-1.5 border border-slate-800/80 text-xs">
        <div className="flex items-center gap-1.5">
          <span className={`h-2.5 w-2.5 rounded-full ${
            !isOnline ? "bg-red-500" : isRecovering ? "bg-amber-400 animate-pulse" : "bg-emerald-400 animate-pulse"
          }`} />
          <span className={`font-bold ${!isOnline ? "text-red-400" : isRecovering ? "text-amber-400" : "text-slate-200"}`}>
            {node.status}
          </span>
        </div>
        <div className="flex items-center gap-1 text-[11px]">
          <span className="text-slate-400">Risk:</span>
          <span className={`font-mono font-black text-xs px-1.5 py-0.5 rounded ${
            node.threat_score >= 70
              ? "bg-red-950/80 text-red-400 border border-red-800/60"
              : node.threat_score >= 40
              ? "bg-amber-950/80 text-amber-400 border border-amber-800/60"
              : "bg-emerald-950/80 text-emerald-400 border border-emerald-800/60"
          }`}>
            {node.threat_score}
          </span>
        </div>
      </div>

      {/* Telemetry Metrics */}
      <div className="mt-2 grid grid-cols-2 gap-2 text-xs bg-slate-950/80 rounded-xl p-2 border border-slate-800/80">
        <div>
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="flex items-center gap-1 text-[10px] font-medium">
              <Cpu className="h-3 w-3 text-slate-400" /> CPU
            </span>
            <span className="font-mono text-slate-100 font-bold text-[11px]">{node.cpu_usage.toFixed(1)}%</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${node.cpu_usage > 70 ? "bg-red-500" : node.cpu_usage > 40 ? "bg-amber-500" : "bg-blue-500"}`}
              style={{ width: `${Math.min(100, Math.max(8, node.cpu_usage))}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="flex items-center gap-1 text-[10px] font-medium">
              <Activity className="h-3 w-3 text-slate-400" /> Traffic
            </span>
            <span className="font-mono text-slate-100 font-bold text-[11px]">{Math.round(node.network_traffic)} pps</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${node.network_traffic > 3000 ? "bg-red-500" : node.network_traffic > 1000 ? "bg-amber-500" : "bg-blue-500"}`}
              style={{ width: `${Math.min(100, Math.max(8, (node.network_traffic / 4000) * 100))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Threat incursion alert banner */}
      {isAttacked && (
        <div className="mt-2 flex items-center gap-1.5 text-xs font-bold text-red-300 bg-red-950/70 border border-red-700/70 rounded-xl px-2.5 py-1 animate-pulse">
          <ShieldAlert className="h-3.5 w-3.5 shrink-0 text-red-400" />
          <span className="truncate uppercase tracking-wide">Threat: {node.current_threat}</span>
        </div>
      )}
    </div>
  );
};
