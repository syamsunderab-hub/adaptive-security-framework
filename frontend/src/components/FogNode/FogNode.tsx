import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Server, Cpu, Activity, ShieldAlert, Network } from "lucide-react";
import { NodeState } from "../../types/node";
import { SecurityLevelBadge } from "../SecurityLevel/SecurityLevelBadge";

interface FogNodeData {
  node: NodeState;
  isSelected?: boolean;
}

export const FogNode: React.FC<{ data: FogNodeData }> = ({ data }) => {
  const { node, isSelected } = data;
  const isOnline = node.status === "ONLINE";
  const isRecovering = node.status === "RECOVERING";
  const isAttacked = node.current_threat !== "NORMAL" && isOnline;

  const borderColor = !isOnline
    ? "border-slate-700 bg-slate-900/60 opacity-60"
    : isAttacked
    ? "border-amber-500 bg-gradient-to-b from-slate-900 via-amber-950/30 to-slate-900 shadow-xl shadow-amber-950/60 ring-2 ring-amber-500/50"
    : isSelected
    ? "border-cyan-400 bg-slate-900 shadow-xl shadow-cyan-950/60 ring-2 ring-cyan-400/60"
    : "border-slate-700/90 bg-slate-900/95 hover:border-slate-500 shadow-lg";

  return (
    <div className={`relative w-[340px] rounded-2xl border p-3.5 backdrop-blur-md transition-all duration-200 cursor-pointer ${borderColor}`}>
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3.5 !h-3.5 !bg-cyan-400 !border-2 !border-slate-950 shadow-md shadow-cyan-500/50"
      />

      {/* Header */}
      <div className="flex items-center justify-between gap-2.5 border-b border-slate-800/90 pb-2.5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-inner">
            <Server className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-black tracking-wide text-slate-100">{node.node_id}</span>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-semibold">
                FOG
              </span>
            </div>
            <div className="text-[11px] text-slate-400 uppercase font-semibold tracking-wider mt-0.5">{node.name}</div>
          </div>
        </div>
        <SecurityLevelBadge level={node.security_level} size="sm" />
      </div>

      {/* Status & Risk Banner */}
      <div className="mt-2.5 flex items-center justify-between rounded-xl bg-slate-950/70 px-2.5 py-1.5 border border-slate-800/80 text-xs">
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${
            !isOnline ? "bg-slate-500" : isRecovering ? "bg-amber-400 animate-pulse" : "bg-cyan-400 animate-pulse"
          }`} />
          <span className="font-bold text-slate-200">
            {node.status}
          </span>
        </div>
        <div className="flex items-center gap-1 text-[11px]">
          <span className="text-slate-400">Risk:</span>
          <span className={`font-mono font-bold text-xs px-1.5 py-0.5 rounded ${
            node.threat_score >= 50 ? "bg-amber-950/80 text-amber-400 border border-amber-800/60" : "bg-cyan-950/80 text-cyan-400 border border-cyan-800/60"
          }`}>
            {node.threat_score}
          </span>
        </div>
      </div>

      {/* Telemetry Metrics */}
      <div className="mt-2.5 grid grid-cols-2 gap-2 text-xs bg-slate-950/80 rounded-xl p-2 border border-slate-800/80">
        <div>
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="flex items-center gap-1 text-[10px] font-medium">
              <Cpu className="h-3 w-3 text-slate-400" /> CPU
            </span>
            <span className="font-mono text-slate-100 font-bold text-[11px]">{node.cpu_usage.toFixed(1)}%</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${node.cpu_usage > 60 ? "bg-amber-500" : "bg-cyan-500"}`}
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
              className={`h-full transition-all duration-300 ${node.network_traffic > 2000 ? "bg-amber-500" : "bg-cyan-500"}`}
              style={{ width: `${Math.min(100, Math.max(8, (node.network_traffic / 3000) * 100))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Threat Flag */}
      {isAttacked && (
        <div className="mt-2 flex items-center gap-1.5 text-xs font-bold text-amber-300 bg-amber-950/60 border border-amber-700/60 rounded-xl px-2.5 py-1 animate-pulse">
          <ShieldAlert className="h-3.5 w-3.5 shrink-0 text-amber-400" />
          <span className="truncate">{node.current_threat}</span>
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3.5 !h-3.5 !bg-cyan-400 !border-2 !border-slate-950 shadow-md shadow-cyan-500/50"
      />
    </div>
  );
};
