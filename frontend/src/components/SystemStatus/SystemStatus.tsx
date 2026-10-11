import React from "react";
import { ShieldCheck, ShieldAlert, Cpu, Network, CheckCircle2, AlertTriangle, Layers, Wifi, WifiOff } from "lucide-react";
import { SystemStatus as SystemStatusType } from "../../types/security";
import { SecurityLevelBadge } from "../SecurityLevel/SecurityLevelBadge";

interface Props {
  status: SystemStatusType | null;
  connected: boolean;
}

export const SystemStatusHeader: React.FC<Props> = ({ status, connected }) => {
  const isFullAdaptation = status?.global_mode === "FULL_ADAPTATION";

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 px-5 py-3 backdrop-blur-md">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Title & Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-600 shadow-md shadow-emerald-950/40 text-slate-950 font-black">
            <Layers className="h-5 w-5 text-slate-950" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black tracking-wider text-slate-100 uppercase">
                Adaptive Security Command Center
              </h1>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                SAFER-D ARCHITECTURE
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Distributed Edge/Fog/Cloud Autonomous Runtime Adaptation Engine
            </p>
          </div>
        </div>

        {/* Global Adaptation Mode Indicator */}
        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end">
            <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
              SYSTEM MODE
            </div>
            <div className="mt-0.5">
              {isFullAdaptation ? (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/70 border border-emerald-500/50 text-emerald-300 font-bold text-xs shadow-lg shadow-emerald-950/50 animate-pulse">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  FULL ADAPTATION
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-950/80 border border-red-500/60 text-red-300 font-bold text-xs shadow-lg shadow-red-950/60 animate-bounce">
                  <AlertTriangle className="h-3.5 w-3.5 text-red-400" />
                  PARTIAL ADAPTATION (DEGRADED)
                </div>
              )}
            </div>
          </div>

          {/* Most Restrictive Level */}
          <div className="flex flex-col items-end pl-3 border-l border-slate-800">
            <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
              MOST RESTRICTIVE
            </div>
            <div className="mt-0.5">
              <SecurityLevelBadge level={status?.most_restrictive_level || "DEFCON_5"} size="md" />
            </div>
          </div>

          {/* WebSocket Link */}
          <div className="flex items-center gap-1.5 pl-3 border-l border-slate-800">
            {connected ? (
              <span className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-800/80 text-[11px] font-mono text-emerald-400 border border-emerald-500/30">
                <Wifi className="h-3 w-3" />
                ONLINE
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-2 py-1 rounded bg-red-950/80 text-[11px] font-mono text-red-400 border border-red-500/30 animate-pulse">
                <WifiOff className="h-3 w-3" />
                DISCONNECTED
              </span>
            )}
          </div>
        </div>
      </div>

      {/* KPI Stats Ribbon */}
      <div className="mt-2.5 flex flex-wrap items-center gap-6 border-t border-slate-800/60 pt-2 text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <span className="text-slate-500">Topology Status:</span>
          <span className="font-mono font-bold text-slate-100">
            {status?.online_nodes || 0} / {status?.total_nodes || 7} Online
          </span>
          {status && status.offline_nodes > 0 && (
            <span className="px-1.5 py-0.2 rounded bg-red-900/40 text-red-400 border border-red-800/50 text-[10px] font-mono">
              {status.offline_nodes} Offline
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">Active Threats:</span>
          <span className={`font-mono font-bold ${(status?.active_threats_count || 0) > 0 ? "text-red-400 font-extrabold" : "text-emerald-400"}`}>
            {status?.active_threats_count || 0}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">Average Risk Score:</span>
          <span className={`font-mono font-bold ${(status?.avg_risk_score || 0) >= 50 ? "text-amber-400" : "text-emerald-400"}`}>
            {status?.avg_risk_score || 0} / 100
          </span>
        </div>

        {/* Group cluster health tags */}
        <div className="ml-auto flex items-center gap-2">
          {status?.active_adaptation_groups?.map((grp) => (
            <div
              key={grp.group_id}
              className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                grp.is_degraded
                  ? "bg-red-950/40 border-red-700/50 text-red-300"
                  : "bg-slate-800/50 border-slate-700/50 text-slate-400"
              }`}
            >
              {grp.name.replace("Fog Cluster ", "Fog ").replace("Cloud Core Backbone", "Cloud")}:{" "}
              <span className="font-semibold text-slate-200">
                {grp.online_members.length}/{grp.total_members}
              </span>
            </div>
          ))}
        </div>
      </div>
    </header>
  );
};
