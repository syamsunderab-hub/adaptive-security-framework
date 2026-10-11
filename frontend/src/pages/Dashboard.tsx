import React, { useState } from "react";
import { useSystemState } from "../hooks/useSystemState";
import { SystemStatusHeader } from "../components/SystemStatus/SystemStatus";
import { NetworkGraph } from "../components/NetworkGraph/NetworkGraph";
import { NodeDetails } from "../components/NodeDetails/NodeDetails";
import { MapeKPanel } from "../components/MapeKPanel/MapeKPanel";
import { ThreatPanel } from "../components/ThreatPanel/ThreatPanel";
import { EventTimeline } from "../components/EventTimeline/EventTimeline";
import { SimulationControls } from "../components/SimulationControls/SimulationControls";
import { ChevronRight, ChevronLeft, Sidebar, Maximize2, Minimize2 } from "lucide-react";

export const Dashboard: React.FC = () => {
  const {
    nodes,
    selectedNodeId,
    setSelectedNodeId,
    selectedNode,
    systemStatus,
    events,
    threats,
    demoProgress,
    connected,
  } = useSystemState();

  const [isTopologyExpanded, setIsTopologyExpanded] = useState(false);

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Top Header & System KPIs */}
      <SystemStatusHeader status={systemStatus} connected={connected} />

      {/* Main Layout Area */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left / Center Main View: Simulation Deck, Topology & MAPE-K */}
        <div className="flex flex-1 flex-col overflow-hidden border-r border-slate-800">
          {/* Simulation Controls Deck - Compact toolbar */}
          <div className="px-3 py-2 border-b border-slate-800/80 bg-slate-950/80 z-10 shrink-0">
            <SimulationControls
              selectedNodeId={selectedNodeId}
              demoProgress={demoProgress}
            />
          </div>

          {/* Central Network Topology Visualizer - Primary Focus Area */}
          <div className="relative flex-1 bg-slate-950 min-h-0">
            <NetworkGraph
              nodes={nodes}
              selectedNodeId={selectedNodeId}
              onSelectNode={setSelectedNodeId}
              isExpanded={isTopologyExpanded}
              onToggleExpand={() => setIsTopologyExpanded(!isTopologyExpanded)}
            />
          </div>

          {/* MAPE-K Autonomous Loop Stage Visualizer - Compact Footer Strip */}
          <div className="px-3 py-2 border-t border-slate-800/80 bg-slate-950/80 z-10 shrink-0">
            <MapeKPanel node={selectedNode} />
          </div>
        </div>

        {/* Right Inspection & Operations Sidebar */}
        <div
          className={`flex flex-col overflow-hidden bg-slate-900/60 border-l border-slate-800/80 transition-all duration-300 ease-in-out ${
            isTopologyExpanded ? "w-0 opacity-0 pointer-events-none" : "w-96 opacity-100"
          }`}
        >
          {/* Node Details Inspection Panel (Top Half) */}
          <div className="h-[52%] border-b border-slate-800/90 overflow-hidden">
            <NodeDetails node={selectedNode} />
          </div>

          {/* Threat Intelligence & Security Event Timeline (Bottom Half) */}
          <div className="grid h-[48%] grid-rows-2 overflow-hidden">
            <div className="border-b border-slate-800/90 overflow-hidden">
              <ThreatPanel threats={threats} />
            </div>
            <div className="overflow-hidden">
              <EventTimeline events={events} />
            </div>
          </div>
        </div>

        {/* Floating Sidebar Toggle Button when collapsed */}
        {isTopologyExpanded && (
          <button
            onClick={() => setIsTopologyExpanded(false)}
            title="Restore Sidebar"
            className="absolute top-4 right-4 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-900/90 hover:bg-slate-800 text-slate-200 text-xs font-bold shadow-xl backdrop-blur-md transition-all"
          >
            <Sidebar className="h-4 w-4 text-emerald-400" />
            <span>Show Sidebar</span>
          </button>
        )}
      </div>
    </div>
  );
};
