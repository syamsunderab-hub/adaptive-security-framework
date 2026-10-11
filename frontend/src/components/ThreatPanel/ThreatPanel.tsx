import React from "react";
import { ShieldAlert, AlertOctagon, AlertTriangle, ShieldCheck } from "lucide-react";
import { ThreatEvent } from "../../types/threat";

interface Props {
  threats: ThreatEvent[];
}

export const ThreatPanel: React.FC<Props> = ({ threats }) => {
  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return "bg-red-950/80 text-red-300 border-red-700/60";
      case "HIGH":
        return "bg-orange-950/80 text-orange-300 border-orange-700/60";
      case "MEDIUM":
        return "bg-amber-950/80 text-amber-300 border-amber-700/60";
      default:
        return "bg-blue-950/80 text-blue-300 border-blue-700/60";
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-2.5">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-3.5 w-3.5 text-red-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Threat Intelligence & Incursions
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slate-400">
          {threats.length} recorded
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {threats.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center text-xs text-slate-500">
            <ShieldCheck className="h-8 w-8 text-emerald-500/40 mb-1" />
            <span>No active intrusions detected. System nominal.</span>
          </div>
        ) : (
          threats.map((th) => (
            <div
              key={th.threat_id}
              className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5 text-xs transition-all hover:border-slate-700"
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5">
                  <span className="font-mono font-bold text-slate-200">{th.threat_type}</span>
                  <span className="text-[10px] font-mono text-slate-400">[{th.node_id}]</span>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getSeverityBadge(th.severity)}`}>
                  {th.severity}
                </span>
              </div>

              <p className="mt-1 text-[11px] text-slate-300">
                {th.description}
              </p>

              <div className="mt-2 flex items-center justify-between pt-1 border-t border-slate-800/60 text-[10px] text-slate-400">
                <span>Confidence: <strong className="text-slate-200 font-mono">{Math.round(th.confidence * 100)}%</strong></span>
                <span className="text-amber-400/90 font-medium truncate max-w-[180px]">{th.recommended_action}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
