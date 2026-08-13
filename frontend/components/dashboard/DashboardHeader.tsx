"use client";

import { motion } from "framer-motion";
import { Activity, Zap, Shield } from "lucide-react";

export function DashboardHeader() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <motion.div className="flex items-center gap-3" initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }}>
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
              PAIOS
            </h1>
            <p className="text-xs text-slate-400">Platform for AI Orchestration & Self-Healing</p>
          </div>
        </motion.div>

        <motion.div className="flex items-center gap-4" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }}>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <Activity className="w-3 h-3 text-emerald-400" />
            <span className="text-xs text-emerald-400 font-medium">System Healthy</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20">
            <Shield className="w-3 h-3 text-blue-400" />
            <span className="text-xs text-blue-400 font-medium">v2.0.0</span>
          </div>
        </motion.div>
      </div>
    </header>
  );
}
