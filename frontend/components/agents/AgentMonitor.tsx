"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Play, Pause, RotateCcw, Heart, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const mockAgents = [
  { id: "1", name: "Code Reviewer", type: "llm", status: "running", health: 0.95, executions: 1240 },
  { id: "2", name: "Data Analyzer", type: "data", status: "idle", health: 0.88, executions: 856 },
  { id: "3", name: "Vision Processor", type: "vision", status: "error", health: 0.45, executions: 432 },
  { id: "4", name: "Release Guard", type: "validator", status: "healing", health: 0.72, executions: 2100 },
];

export function AgentMonitor() {
  const [agents, setAgents] = useState(mockAgents);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "idle": return "text-slate-400 bg-slate-500/10 border-slate-500/20";
      case "error": return "text-red-400 bg-red-500/10 border-red-500/20";
      case "healing": return "text-amber-400 bg-amber-500/10 border-amber-500/20 animate-pulse";
      default: return "text-slate-400";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Agent Monitor</h2>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Bot className="w-4 h-4 mr-2" /> Deploy Agent
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AnimatePresence>
          {agents.map((agent, i) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-xl p-5 border border-slate-800 bg-slate-900/50 hover:border-slate-700 transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${getStatusColor(agent.status)}`}>
                    <Bot className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{agent.name}</h3>
                    <p className="text-xs text-slate-400 uppercase">{agent.type}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
                  {agent.status}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400 flex items-center gap-1">
                    <Heart className="w-3 h-3" /> Health Score
                  </span>
                  <span className={agent.health > 0.8 ? "text-emerald-400" : agent.health > 0.5 ? "text-amber-400" : "text-red-400"}>
                    {Math.round(agent.health * 100)}%
                  </span>
                </div>
                <Progress value={agent.health * 100} className="h-2" />
              </div>

              <div className="flex items-center justify-between text-sm text-slate-400 mb-4">
                <span>Executions: {agent.executions.toLocaleString()}</span>
                {agent.status === "error" && (
                  <span className="flex items-center gap-1 text-red-400">
                    <AlertCircle className="w-3 h-3" /> Self-healing triggered
                  </span>
                )}
              </div>

              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1 border-slate-700 hover:bg-slate-800">
                  <Play className="w-3 h-3 mr-1" /> Run
                </Button>
                <Button variant="outline" size="sm" className="flex-1 border-slate-700 hover:bg-slate-800">
                  <Pause className="w-3 h-3 mr-1" /> Pause
                </Button>
                <Button variant="outline" size="sm" className="flex-1 border-slate-700 hover:bg-slate-800">
                  <RotateCcw className="w-3 h-3 mr-1" /> Restart
                </Button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
