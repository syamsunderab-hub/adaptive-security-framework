import React from "react";
import { Check, Loader2, Circle, Database, Brain } from "lucide-react";
import { NodeState, MapeKStage } from "../../types/node";

interface Props {
  node: NodeState | null;
}

export const MapeKPanel: React.FC<{ node: NodeState | null }> = ({ node }) => {
  const stage = node?.mape_k_stage || "IDLE";

  const stages: { key: MapeKStage; name: string; desc: string }[] = [
    { key: "MONITOR", name: "Monitor (M)", desc: "Telemetry Ingestion" },
    { key: "ANALYZE", name: "Analyze (A)", desc: "Threat Anomaly Scoring" },
    { key: "PLAN", name: "Plan (P)", desc: "DEFCON Policy Synthesis" },
    { key: "EXECUTE", name: "Execute (E)", desc: "Posture Enforcement" },
  ];

  const getStageStatus = (stepKey: MapeKStage) => {
    if (stage === "IDLE") return "inactive";
    const order: MapeKStage[] = ["MONITOR", "ANALYZE", "PLAN", "EXECUTE"];
    const currentIndex = order.indexOf(stage);
    const stepIndex = order.indexOf(stepKey);

    if (stepIndex < currentIndex) return "completed";
    if (stepIndex === currentIndex) return "active";
    return "pending";
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/90 px-4 py-2.5 backdrop-blur-md shadow-md">
      {/* Title & Active Node */}
      <div className="flex items-center gap-2.5 shrink-0">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
          <Brain className="h-4 w-4" />
        </div>
        <div>
          <div className="text-xs font-black uppercase tracking-wider text-slate-200">
            MAPE-K Loop
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            Node: <span className="font-bold text-slate-200">{node?.node_id || "ALL"}</span>
          </div>
        </div>
      </div>

      {/* 4 Loop Stages in Sleek Horizontal Row */}
      <div className="grid grid-cols-4 gap-2 flex-1 max-w-2xl">
        {stages.map((st) => {
          const status = getStageStatus(st.key);
          const isAct = status === "active";
          const isDone = status === "completed";

          return (
            <div
              key={st.key}
              className={`flex items-center gap-2 rounded-lg border px-2.5 py-1.5 transition-all ${
                isAct
                  ? "border-emerald-500 bg-emerald-950/50 text-emerald-300 shadow-md shadow-emerald-950/40 ring-1 ring-emerald-500/40"
                  : isDone
                  ? "border-slate-700 bg-slate-900/80 text-slate-300"
                  : "border-slate-800/80 bg-slate-950/40 text-slate-500"
              }`}
            >
              <div className="flex items-center justify-center shrink-0">
                {isAct ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-emerald-400" />
                ) : isDone ? (
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                ) : (
                  <Circle className="h-2.5 w-2.5 text-slate-600" />
                )}
              </div>
              <div className="min-w-0">
                <div className="text-[11px] font-bold uppercase tracking-wide truncate">{st.name}</div>
                <div className="text-[9px] text-slate-400 truncate hidden md:block">{st.desc}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Knowledge Base Badge */}
      <div className="hidden lg:flex items-center gap-1.5 rounded-lg bg-slate-950/80 px-2.5 py-1.5 border border-slate-800 text-[10px] text-slate-400 shrink-0">
        <Database className="h-3.5 w-3.5 text-cyan-400" />
        <span className="font-medium text-slate-300">Shared Knowledge Base (K) Synced</span>
      </div>
    </div>
  );
};
