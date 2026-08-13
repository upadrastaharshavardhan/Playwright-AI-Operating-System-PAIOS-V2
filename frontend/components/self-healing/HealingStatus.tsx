"use client";

import { motion } from "framer-motion";
import { Shield, CheckCircle, XCircle, Activity } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const healingLog = [
  { id: 1, agent: "Vision Processor", issue: "Context overflow", strategy: "Token reduction", status: "success", time: "2m ago" },
  { id: 2, agent: "Code Reviewer", issue: "Rate limit hit", strategy: "Exponential backoff", status: "success", time: "15m ago" },
  { id: 3, agent: "Data Analyzer", issue: "Model error", strategy: "Model fallback", status: "failed", time: "1h ago" },
];

export function HealingStatus() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Shield className="w-6 h-6 text-emerald-400" />
          Self-Healing Status
        </h2>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <Activity className="w-3 h-3 text-emerald-400" />
          <span className="text-xs text-emerald-400">Auto-Healing Enabled</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 text-center">
          <div className="text-3xl font-bold text-emerald-400">94%</div>
          <div className="text-sm text-slate-400 mt-1">Success Rate</div>
        </motion.div>
        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} transition={{ delay: 0.1 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 text-center">
          <div className="text-3xl font-bold text-blue-400">1.2s</div>
          <div className="text-sm text-slate-400 mt-1">Avg Recovery Time</div>
        </motion.div>
        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} transition={{ delay: 0.2 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 text-center">
          <div className="text-3xl font-bold text-violet-400">24</div>
          <div className="text-sm text-slate-400 mt-1">Interventions Today</div>
        </motion.div>
      </div>

      <div className="rounded-xl overflow-hidden bg-slate-900/50 border border-slate-800">
        <div className="p-4 border-b border-slate-800">
          <h3 className="font-semibold text-white">Healing Log</h3>
        </div>
        <div className="divide-y divide-slate-800">
          {healingLog.map((log, i) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.1 }}
              className="p-4 flex items-center justify-between hover:bg-slate-800/30"
            >
              <div className="flex items-center gap-3">
                {log.status === "success" ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <XCircle className="w-5 h-5 text-red-400" />}
                <div>
                  <p className="text-sm font-medium text-white">{log.agent}</p>
                  <p className="text-xs text-slate-400">{log.issue} &rarr; {log.strategy}</p>
                </div>
              </div>
              <span className="text-xs text-slate-500">{log.time}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
