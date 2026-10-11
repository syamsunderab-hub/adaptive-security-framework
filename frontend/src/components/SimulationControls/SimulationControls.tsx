import React, { useState } from "react";
import {
  Play,
  Square,
  Flame,
  Search,
  KeyRound,
  RotateCcw,
  Sparkles,
  Power,
  CheckCircle2,
  SlidersHorizontal
} from "lucide-react";
import { DemoProgress } from "../../types/security";
import {
  startSimulation,
  stopSimulation,
  resetSimulation,
  triggerAttack,
  failNode,
  recoverNode,
  triggerFullDemo
} from "../../services/api";

interface Props {
  selectedNodeId: string | null;
  demoProgress: DemoProgress | null;
}

export const SimulationControls: React.FC<Props> = ({ selectedNodeId, demoProgress }) => {
  const [isRunning, setIsRunning] = useState(true);
  const [loading, setLoading] = useState<string | null>(null);

  const targetNode = selectedNodeId || "EDGE-02";

  const handleStartStop = async () => {
    setLoading("toggle");
    try {
      if (isRunning) {
        await stopSimulation();
        setIsRunning(false);
      } else {
        await startSimulation();
        setIsRunning(true);
      }
    } finally {
      setLoading(null);
    }
  };

  const handleAttack = async (type: "ICMP_FLOOD" | "PORT_SCAN" | "BRUTE_FORCE_AUTH") => {
    setLoading(type);
    try {
      await triggerAttack(targetNode, type);
    } finally {
      setLoading(null);
    }
  };

  const handleFail = async () => {
    setLoading("fail");
    try {
      await failNode(targetNode);
    } finally {
      setLoading(null);
    }
  };

  const handleRecover = async () => {
    setLoading("recover");
    try {
      await recoverNode(targetNode);
    } finally {
      setLoading(null);
    }
  };

  const handleReset = async () => {
    setLoading("reset");
    try {
      await resetSimulation();
    } finally {
      setLoading(null);
    }
  };

  const handleDemo = async () => {
    setLoading("demo");
    try {
      await triggerFullDemo();
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="flex flex-col gap-2 rounded-xl border border-slate-800 bg-slate-900/95 px-3 py-2.5 backdrop-blur-md shadow-md">
      {/* Streamlined Single-Row Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        {/* Left: Section Label & Target Node Badge */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs font-black uppercase tracking-wider text-slate-200">
            <SlidersHorizontal className="h-3.5 w-3.5 text-teal-400" />
            <span className="hidden sm:inline">Simulation Deck</span>
          </div>
          <div className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950/80 px-2 py-1 text-[11px]">
            <span className="text-slate-400 font-medium">Target:</span>
            <span className="font-mono font-black text-emerald-400">{targetNode}</span>
          </div>
        </div>

        {/* Center: Compact Action Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
          <button
            onClick={handleStartStop}
            title={isRunning ? "Pause Telemetry Simulation" : "Resume Telemetry Simulation"}
            className={`flex items-center gap-1 rounded-lg border px-2.5 py-1.5 transition-colors ${
              isRunning
                ? "bg-slate-800/80 hover:bg-slate-800 text-slate-300 border-slate-700"
                : "bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border-emerald-600"
            }`}
          >
            {isRunning ? <Square className="h-3 w-3 text-amber-400" /> : <Play className="h-3 w-3 text-emerald-400" />}
            <span className="hidden md:inline">{isRunning ? "Pause" : "Start"}</span>
          </button>

          <button
            onClick={() => handleAttack("ICMP_FLOOD")}
            disabled={loading !== null}
            title="Inject massive packet flood on target node"
            className="flex items-center gap-1 rounded-lg border border-red-800/60 bg-red-950/40 hover:bg-red-900/60 text-red-200 px-2.5 py-1.5 transition-colors"
          >
            <Flame className="h-3 w-3 text-red-400" />
            <span>ICMP Flood</span>
          </button>

          <button
            onClick={() => handleAttack("PORT_SCAN")}
            disabled={loading !== null}
            title="Simulate rapid TCP port scan anomaly"
            className="flex items-center gap-1 rounded-lg border border-orange-800/60 bg-orange-950/40 hover:bg-orange-900/60 text-orange-200 px-2.5 py-1.5 transition-colors"
          >
            <Search className="h-3 w-3 text-orange-400" />
            <span className="hidden lg:inline">Port Scan</span>
          </button>

          <button
            onClick={() => handleAttack("BRUTE_FORCE_AUTH")}
            disabled={loading !== null}
            title="Simulate credential brute-force attack"
            className="flex items-center gap-1 rounded-lg border border-purple-800/60 bg-purple-950/40 hover:bg-purple-900/60 text-purple-200 px-2.5 py-1.5 transition-colors"
          >
            <KeyRound className="h-3 w-3 text-purple-400" />
            <span className="hidden lg:inline">Auth Attack</span>
          </button>

          <button
            onClick={handleFail}
            disabled={loading !== null}
            title="Terminate node heartbeat to trigger timeout and Partial Adaptation"
            className="flex items-center gap-1 rounded-lg border border-red-700/80 bg-red-950/70 hover:bg-red-900 text-red-300 px-2.5 py-1.5 transition-colors"
          >
            <Power className="h-3 w-3 text-red-400" />
            <span>Fail</span>
          </button>

          <button
            onClick={handleRecover}
            disabled={loading !== null}
            title="Restore node heartbeat and trigger reintegration to Full Adaptation"
            className="flex items-center gap-1 rounded-lg border border-emerald-700/80 bg-emerald-950/70 hover:bg-emerald-900 text-emerald-300 px-2.5 py-1.5 transition-colors"
          >
            <CheckCircle2 className="h-3 w-3 text-emerald-400" />
            <span>Recover</span>
          </button>

          <button
            onClick={handleReset}
            disabled={loading !== null}
            title="Reset all 7 nodes to DEFCON 5 baseline and Full Adaptation"
            className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 transition-colors"
          >
            <RotateCcw className="h-3 w-3 text-cyan-400" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        </div>

        {/* Right: Primary Demo Button */}
        <button
          onClick={handleDemo}
          disabled={demoProgress !== null || loading === "demo"}
          title="Run the complete automated 11-step demo scenario"
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-500 to-cyan-500 px-3.5 py-1.5 text-xs font-black uppercase tracking-wider text-slate-950 shadow-md shadow-emerald-950/60 hover:brightness-110 active:scale-95 disabled:opacity-50 transition-all shrink-0"
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span>RUN FULL DEMO</span>
        </button>
      </div>

      {/* Compact Demo Progress Bar (only shown during active demo) */}
      {demoProgress && (
        <div className="rounded-lg border border-cyan-500/50 bg-cyan-950/40 px-3 py-2 animate-pulse text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-cyan-200">
              Demo Execution: Step {demoProgress.current_step} of {demoProgress.total_steps}
            </span>
            <span className="font-mono text-[11px] font-bold text-cyan-400">
              {Math.round((demoProgress.current_step / demoProgress.total_steps) * 100)}%
            </span>
          </div>
          <div className="mt-1.5 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-300"
              style={{ width: `${(demoProgress.current_step / demoProgress.total_steps) * 100}%` }}
            />
          </div>
          <p className="mt-1 text-[11px] text-cyan-300/90 font-medium truncate">
            {demoProgress.status_text}
          </p>
        </div>
      )}
    </div>
  );
};
