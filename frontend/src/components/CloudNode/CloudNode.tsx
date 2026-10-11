import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Cloud, Cpu, Activity, ShieldAlert, Network, AlertCircle, Wifi } from "lucide-react";
import { NodeState } from "../../types/node";
import { SecurityLevelBadge } from "../SecurityLevel/SecurityLevelBadge";

interface CloudNodeData {
  node: NodeState;
  isSelected?: boolean;
}

export const CloudNode: React.FC<{ data: CloudNodeData }> = ({ data }) => {
  const { node, isSelected } = data;
  const isOnline = node.status === "ONLINE";
  const isRecovering = node.status === "RECOVERING";
  const isAttacked = node.current_threat !== "NORMAL" && isOnline;

  const borderColor = !isOnline
    ? "border-slate-700 bg-slate-900/60 opacity-60"
    : isAttacked
    ? "border-red-500 bg-gradient-to-b from-slate-900 via-red-950/30 to-slate-900 shadow-2xl shadow-red-950/70 ring-2 ring-red-500/50"
    : isSelected
    ? "border-emerald-400 bg-slate-900 shadow-xl shadow-emerald-950/60 ring-2 ring-emerald-400/60"
    : "border-slate-700/90 bg-slate-900/95 hover:border-slate-500 shadow-lg";

  return (
    <div className={`relative w-[380px] rounded-2xl border p-4 backdrop-blur-md transition-all duration-200 cursor-pointer ${borderColor}`}>
      {/* Node Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-800/90 pb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-inner">
            <Cloud className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-black tracking-wider text-slate-100 uppercase">{node.node_id}</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-semibold">
                ROOT CORE
              </span>
            </div>
            <div className="text-xs text-slate-400 font-semibold tracking-wide mt-0.5">Cloud Master Controller</div>
          </div>
        </div>
        <SecurityLevelBadge level={node.security_level} size="md" />
      </div>

      {/* Status & Risk Banner */}
      <div className="mt-3 flex items-center justify-between rounded-xl bg-slate-950/70 px-3 py-2 border border-slate-800/80">
        <div className="flex items-center gap-2 text-xs">
          <span className={`h-2.5 w-2.5 rounded-full ${
            !isOnline ? "bg-slate-500" : isRecovering ? "bg-amber-400 animate-pulse" : "bg-emerald-400 animate-pulse"
          }`} />
          <span className="font-bold text-slate-200">
            {node.status}
          </span>
          <span className="text-[11px] text-slate-400 font-mono">
            ({node.heartbeat_status})
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-slate-400 font-medium">Risk Score:</span>
          <span className={`font-mono font-black text-sm px-2 py-0.5 rounded-md ${
            node.threat_score >= 70
              ? "bg-red-950/80 text-red-400 border border-red-800/60"
              : node.threat_score >= 40
              ? "bg-amber-950/80 text-amber-400 border border-amber-800/60"
              : "bg-emerald-950/80 text-emerald-400 border border-emerald-800/60"
          }`}>
            {node.threat_score} / 100
          </span>
        </div>
      </div>

      {/* Telemetry Metrics Panel */}
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs bg-slate-950/80 rounded-xl p-2.5 border border-slate-800/80">
        <div>
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="flex items-center gap-1.5 text-[11px] font-medium">
              <Cpu className="h-3.5 w-3.5 text-slate-400" /> CPU Load
            </span>
            <span className="font-mono text-slate-100 font-bold text-xs">{node.cpu_usage.toFixed(1)}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${node.cpu_usage > 70 ? "bg-red-500" : node.cpu_usage > 40 ? "bg-amber-500" : "bg-emerald-500"}`}
              style={{ width: `${Math.min(100, Math.max(8, node.cpu_usage))}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="flex items-center gap-1.5 text-[11px] font-medium">
              <Activity className="h-3.5 w-3.5 text-slate-400" /> Network Flow
            </span>
            <span className="font-mono text-slate-100 font-bold text-xs">{Math.round(node.network_traffic).toLocaleString()} pps</span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${node.network_traffic > 3000 ? "bg-red-500" : node.network_traffic > 1000 ? "bg-amber-500" : "bg-cyan-500"}`}
              style={{ width: `${Math.min(100, Math.max(8, (node.network_traffic / 5000) * 100))}%` }}
            />
          </div>
        </div>

        <div className="col-span-2 pt-1 border-t border-slate-800/60 flex justify-between items-center text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <Network className="h-3.5 w-3.5 text-slate-500" /> Sockets: <strong className="text-slate-200 font-mono">{node.connections}</strong>
          </span>
          <span className="font-mono text-[10px] text-slate-400">
            MAPE-K: <strong className="text-emerald-400">{node.mape_k_stage}</strong>
          </span>
        </div>
      </div>

      {/* Threat Flag */}
      {isAttacked && (
        <div className="mt-2.5 flex items-center gap-2 text-xs font-bold text-red-300 bg-red-950/60 border border-red-700/60 rounded-xl px-2.5 py-1.5 animate-pulse">
          <ShieldAlert className="h-4 w-4 shrink-0 text-red-400" />
          <span className="truncate uppercase tracking-wide">Threat: {node.current_threat}</span>
        </div>
      )}

      {/* React Flow output handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-4 !h-4 !bg-emerald-400 !border-2 !border-slate-950 shadow-md shadow-emerald-500/50"
      />
    </div>
  );
};
