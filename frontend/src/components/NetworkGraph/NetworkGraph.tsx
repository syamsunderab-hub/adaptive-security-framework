import React, { useMemo, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
  ReactFlowProvider,
  useReactFlow
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Crosshair,
  ShieldAlert,
  Activity,
  Layers,
  Sparkles
} from "lucide-react";

import { CloudNode } from "../CloudNode/CloudNode";
import { FogNode } from "../FogNode/FogNode";
import { EdgeNode } from "../EdgeNode/EdgeNode";
import { NodeState } from "../../types/node";

interface Props {
  nodes: Record<string, NodeState>;
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

const nodeTypes = {
  cloudNode: CloudNode,
  fogNode: FogNode,
  edgeNode: EdgeNode,
};

// Generously spaced hierarchical coordinates
const fixedPositions: Record<string, { x: number; y: number }> = {
  "CLOUD": { x: 520, y: 35 },
  "FOG-01": { x: 190, y: 260 },
  "FOG-02": { x: 890, y: 260 },
  "EDGE-01": { x: 40, y: 500 },
  "EDGE-02": { x: 370, y: 500 },
  "EDGE-03": { x: 730, y: 500 },
  "EDGE-04": { x: 1060, y: 500 },
};

const edgeConnections = [
  { id: "e-cloud-fog1", source: "CLOUD", target: "FOG-01" },
  { id: "e-cloud-fog2", source: "CLOUD", target: "FOG-02" },
  { id: "e-fog1-edge1", source: "FOG-01", target: "EDGE-01" },
  { id: "e-fog1-edge2", source: "FOG-01", target: "EDGE-02" },
  { id: "e-fog2-edge3", source: "FOG-02", target: "EDGE-03" },
  { id: "e-fog2-edge4", source: "FOG-02", target: "EDGE-04" },
];

const AutoFitHandler: React.FC<{ isExpanded?: boolean }> = ({ isExpanded }) => {
  const { fitView } = useReactFlow();

  useEffect(() => {
    const timer = setTimeout(() => {
      fitView({ padding: 0.08, duration: 400 });
    }, 150);
    return () => clearTimeout(timer);
  }, [isExpanded, fitView]);

  return null;
};

const GraphInner: React.FC<Props> = ({
  nodes,
  selectedNodeId,
  onSelectNode,
  isExpanded = false,
  onToggleExpand
}) => {
  const { fitView, zoomIn, zoomOut } = useReactFlow();

  const flowNodes: Node[] = useMemo(() => {
    return Object.values(nodes).map((n) => {
      const type = n.node_type === "CLOUD" ? "cloudNode" : n.node_type === "FOG" ? "fogNode" : "edgeNode";
      const pos = fixedPositions[n.node_id] || { x: 100, y: 100 };
      return {
        id: n.node_id,
        type,
        position: pos,
        data: {
          node: n,
          isSelected: n.node_id === selectedNodeId,
        },
      };
    });
  }, [nodes, selectedNodeId]);

  const flowEdges: Edge[] = useMemo(() => {
    return edgeConnections.map((conn) => {
      const src = nodes[conn.source];
      const tgt = nodes[conn.target];
      const isSrcOnline = src?.status === "ONLINE";
      const isTgtOnline = tgt?.status === "ONLINE";
      const isBroken = !isSrcOnline || !isTgtOnline;
      const isUnderAttack = (tgt?.current_threat !== "NORMAL" && isTgtOnline) || (src?.current_threat !== "NORMAL" && isSrcOnline);
      const isElevated = (tgt?.security_level !== "DEFCON_5" && tgt?.security_level !== "DEFCON_4") || (src?.security_level !== "DEFCON_5" && src?.security_level !== "DEFCON_4");

      let strokeColor = "#10b981"; // emerald green
      let strokeWidth = 3.5;
      let animated = true;
      let strokeDasharray: string | undefined = undefined;

      if (isBroken) {
        strokeColor = "#64748b"; // muted slate
        strokeWidth = 2.5;
        animated = false;
        strokeDasharray = "6,6";
      } else if (isUnderAttack) {
        strokeColor = "#ef4444"; // red
        strokeWidth = 4.5;
        animated = true;
      } else if (isElevated) {
        strokeColor = "#f59e0b"; // amber
        strokeWidth = 4;
        animated = true;
      }

      return {
        id: conn.id,
        source: conn.source,
        target: conn.target,
        type: "smoothstep",
        animated,
        style: {
          stroke: strokeColor,
          strokeWidth,
          strokeDasharray,
          filter: isUnderAttack ? "drop-shadow(0 0 6px rgba(239, 68, 68, 0.6))" : isElevated ? "drop-shadow(0 0 5px rgba(245, 158, 11, 0.5))" : "drop-shadow(0 0 4px rgba(16, 185, 129, 0.4))",
          transition: "stroke 0.3s, stroke-width 0.3s"
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: 16,
          height: 16,
        },
      };
    });
  }, [nodes]);

  return (
    <div className="relative h-full w-full bg-slate-950 overflow-hidden select-none">
      <AutoFitHandler isExpanded={isExpanded} />

      {/* Floating Topology Controls & Legend Bar */}
      <div className="absolute top-3 left-3 right-3 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        {/* Left: Topology Title & Active Node */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/90 px-3.5 py-1.5 backdrop-blur-md shadow-lg">
            <Layers className="h-4 w-4 text-emerald-400" />
            <span className="text-xs font-black uppercase tracking-wider text-slate-100">
              Distributed Topology Canvas
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
              7 Active Nodes
            </span>
          </div>

          {selectedNodeId && (
            <div className="hidden sm:flex items-center gap-1.5 rounded-xl border border-blue-800/60 bg-blue-950/70 px-3 py-1.5 backdrop-blur-md shadow-md text-xs text-blue-200">
              <span className="text-slate-400">Selected:</span>
              <span className="font-mono font-black text-blue-300">{selectedNodeId}</span>
            </div>
          )}
        </div>

        {/* Right: Legend & Viewport Actions */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Quick Legend */}
          <div className="hidden md:flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/90 px-3 py-1.5 backdrop-blur-md shadow-lg text-[11px] text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" /> Normal Flow
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-amber-400" /> Elevated
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-red-400 animate-ping" /> Threat
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-slate-500" /> Offline
            </span>
          </div>

          {/* Quick Zoom Buttons */}
          <div className="flex items-center rounded-xl border border-slate-800 bg-slate-900/90 p-1 backdrop-blur-md shadow-lg text-slate-300">
            <button
              onClick={() => zoomIn({ duration: 250 })}
              title="Zoom In"
              className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              onClick={() => zoomOut({ duration: 250 })}
              title="Zoom Out"
              className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <button
              onClick={() => fitView({ padding: 0.08, duration: 300 })}
              title="Fit to Center"
              className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-emerald-400 transition-colors"
            >
              <Crosshair className="h-4 w-4" />
            </button>
          </div>

          {/* Fullscreen / Expand Toggle */}
          {onToggleExpand && (
            <button
              onClick={onToggleExpand}
              title={isExpanded ? "Collapse View" : "Maximize Network Canvas"}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border font-bold text-xs backdrop-blur-md shadow-lg transition-all ${
                isExpanded
                  ? "bg-emerald-950 border-emerald-500 text-emerald-200 hover:bg-emerald-900 ring-2 ring-emerald-500/40"
                  : "bg-slate-900/90 border-slate-700 text-slate-200 hover:bg-slate-800 hover:border-slate-500"
              }`}
            >
              {isExpanded ? (
                <>
                  <Minimize2 className="h-4 w-4 text-emerald-400" />
                  <span>Collapse</span>
                </>
              ) : (
                <>
                  <Maximize2 className="h-4 w-4 text-slate-300" />
                  <span>Maximize</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        fitView
        fitViewOptions={{ padding: 0.08, duration: 400 }}
        minZoom={0.35}
        maxZoom={2.0}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1e293b" gap={24} size={1.2} />
        <Controls className="!bg-slate-900/95 !border-slate-800 !text-slate-300 !bottom-4 !left-4" />
        <MiniMap
          nodeColor={(n) => {
            const nodeState = nodes[n.id];
            if (!nodeState || nodeState.status !== "ONLINE") return "#64748b";
            if (nodeState.current_threat !== "NORMAL") return "#ef4444";
            if (nodeState.node_type === "CLOUD") return "#10b981";
            if (nodeState.node_type === "FOG") return "#06b6d4";
            return "#3b82f6";
          }}
          className="!bg-slate-900/95 !border-slate-800 rounded-xl overflow-hidden !bottom-4 !right-4 shadow-xl"
          maskColor="rgba(2, 6, 23, 0.75)"
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  );
};

export const NetworkGraph: React.FC<Props> = (props) => {
  return (
    <ReactFlowProvider>
      <GraphInner {...props} />
    </ReactFlowProvider>
  );
};
