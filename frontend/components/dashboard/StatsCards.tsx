"use client";

import { motion } from "framer-motion";
import { Bot, Workflow, AlertTriangle, TrendingUp } from "lucide-react";

const stats = [
  { label: "Active Agents", value: "24", change: "+12%", icon: Bot, color: "blue" },
  { label: "Workflows", value: "156", change: "+8%", icon: Workflow, color: "violet" },
  { label: "Alerts", value: "3", change: "-25%", icon: AlertTriangle, color: "amber" },
  { label: "Success Rate", value: "99.2%", change: "+0.5%", icon: TrendingUp, color: "emerald" },
];

export function StatsCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, i) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors"
        >
          <div className="flex items-center justify-between mb-4">
            <div className={`p-2 rounded-lg bg-${stat.color}-500/10`}>
              <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
            </div>
            <span className={`text-xs font-medium ${stat.change.startsWith("+") ? "text-emerald-400" : "text-red-400"}`}>
              {stat.change}
            </span>
          </div>
          <div className="text-2xl font-bold text-white">{stat.value}</div>
          <div className="text-sm text-slate-400 mt-1">{stat.label}</div>
        </motion.div>
      ))}
    </div>
  );
}
