import React from "react";
import { Clock, ShieldAlert, AlertTriangle, CheckCircle, Info, Radio } from "lucide-react";
import { SystemEvent } from "../../types/event";

interface Props {
  events: SystemEvent[];
}

export const EventTimeline: React.FC<Props> = ({ events }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return <AlertTriangle className="h-3.5 w-3.5 text-red-400 shrink-0" />;
      case "WARNING":
        return <ShieldAlert className="h-3.5 w-3.5 text-amber-400 shrink-0" />;
      case "SUCCESS":
        return <CheckCircle className="h-3.5 w-3.5 text-emerald-400 shrink-0" />;
      default:
        return <Info className="h-3.5 w-3.5 text-blue-400 shrink-0" />;
    }
  };

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "border-red-900/60 bg-red-950/20 text-red-200";
      case "WARNING":
        return "border-amber-900/60 bg-amber-950/20 text-amber-200";
      case "SUCCESS":
        return "border-emerald-900/60 bg-emerald-950/20 text-emerald-200";
      default:
        return "border-slate-800/80 bg-slate-900/40 text-slate-300";
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Clock className="h-3.5 w-3.5 text-slate-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Security Event Timeline
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slate-400">
          {events.length} events logged
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {events.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">
            Awaiting live security telemetry events...
          </div>
        ) : (
          events.map((evt) => (
            <div
              key={evt.id}
              className={`flex items-start gap-2.5 rounded-lg border p-2 text-xs transition-all ${getSeverityStyle(evt.severity)}`}
            >
              <div className="mt-0.5">{getSeverityIcon(evt.severity)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    {evt.node_id && (
                      <span className="font-mono font-bold text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-200 border border-slate-700">
                        {evt.node_id}
                      </span>
                    )}
                    <span className="font-mono text-[10px] text-slate-400">
                      {evt.formatted_time}
                    </span>
                  </div>
                  <span className="text-[9px] font-mono uppercase tracking-wider px-1 rounded bg-slate-950/60 text-slate-400">
                    {evt.event_type.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-200 leading-snug">
                  {evt.message}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
