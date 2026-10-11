import React from "react";
import { SecurityLevel } from "../../types/node";

interface Props {
  level: SecurityLevel;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export const SecurityLevelBadge: React.FC<Props> = ({ level, size = "md", showLabel = true }) => {
  const configs: Record<SecurityLevel, { label: string; text: string; bg: string; border: string; glow: string }> = {
    DEFCON_5: {
      label: "DEFCON 5",
      text: "text-emerald-400",
      bg: "bg-emerald-950/60",
      border: "border-emerald-500/40",
      glow: "shadow-emerald-900/30"
    },
    DEFCON_4: {
      label: "DEFCON 4",
      text: "text-blue-400",
      bg: "bg-blue-950/60",
      border: "border-blue-500/40",
      glow: "shadow-blue-900/30"
    },
    DEFCON_3: {
      label: "DEFCON 3",
      text: "text-amber-400",
      bg: "bg-amber-950/60",
      border: "border-amber-500/40",
      glow: "shadow-amber-900/30"
    },
    DEFCON_2: {
      label: "DEFCON 2",
      text: "text-orange-400",
      bg: "bg-orange-950/60",
      border: "border-orange-500/40",
      glow: "shadow-orange-900/30"
    },
    DEFCON_1: {
      label: "DEFCON 1",
      text: "text-red-400",
      bg: "bg-red-950/60",
      border: "border-red-500/40",
      glow: "shadow-red-900/40"
    }
  };

  const c = configs[level] || configs.DEFCON_5;
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-xs px-2.5 py-1 font-semibold",
    lg: "text-sm px-3.5 py-1.5 font-bold tracking-wide"
  }[size];

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border shadow-sm ${c.bg} ${c.border} ${c.text} ${c.glow} ${sizeClasses}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${level === "DEFCON_1" || level === "DEFCON_2" ? "animate-ping" : ""} bg-current`} />
      {showLabel ? c.label : level.replace("DEFCON_", "D")}
    </span>
  );
};
