"use client";

import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const alerts = [
  { id: 1, severity: "critical", message: "Agent health dropped below 50%", time: "2m ago", status: "firing" },
  { id: 2, severity: "warning", message: "High latency detected in workflow-3", time: "15m ago", status: "acknowledged" },
  { id: 3, severity: "info", message: "Release v2.1.0 deployed successfully", time: "1h ago", status: "resolved" },
  { id: 4, severity: "critical", message: "Self-healing triggered for Vision Processor", time: "2h ago", status: "resolved" },
];

export function AlertTimeline() {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-500/10 text-red-400 border-red-500/20";
      case "warning": return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "info": return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      default: return "bg-slate-500/10 text-slate-400";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Alert Timeline</h2>
        <div className="flex gap-2">
          {["all", "critical", "warning", "info"].map((f) => (
            <button key={f} className="px-3 py-1 rounded-full text-xs border border-slate-700 hover:bg-slate-800 capitalize text-slate-300">
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-px bg-slate-800" />
        <div className="space-y-4">
          {alerts.map((alert, i) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="relative pl-10"
            >
              <div className={`absolute left-2 top-4 w-4 h-4 rounded-full border-2 ${alert.status === "resolved" ? "bg-emerald-500 border-emerald-500" : alert.severity === "critical" ? "bg-red-500 border-red-500 animate-pulse" : "bg-amber-500 border-amber-500"}`} />
              <div className="rounded-xl p-4 border border-slate-800 bg-slate-900/50">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className={`w-4 h-4 ${alert.severity === "critical" ? "text-red-400" : "text-amber-400"}`} />
                    <span className="text-sm font-medium text-white">{alert.message}</span>
                  </div>
                  <Badge variant="outline" className={getSeverityColor(alert.severity)}>
                    {alert.severity}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {alert.time}</span>
                  <span className="flex items-center gap-1">
                    {alert.status === "resolved" ? <CheckCircle className="w-3 h-3 text-emerald-400" /> : null}
                    {alert.status}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
