"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Users, Plus, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const mockSwarm = {
  id: "swarm-001",
  agents: [
    { role: "coordinator", name: "Coordinator Alpha", status: "active" },
    { role: "worker", name: "Worker-1", status: "active" },
    { role: "worker", name: "Worker-2", status: "active" },
    { role: "critic", name: "Critic Beta", status: "active" },
    { role: "validator", name: "Validator Gamma", status: "idle" },
  ],
};

export function SwarmControl() {
  const [task, setTask] = useState("");
  const [messages, setMessages] = useState<{role: string; content: string}[]>([]);

  const executeTask = () => {
    if (!task) return;
    setMessages(prev => [...prev, { role: "user", content: task }]);
    setTimeout(() => {
      setMessages(prev => [...prev, { role: "swarm", content: `Swarm consensus reached for: ${task}` }]);
    }, 1500);
    setTask("");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Users className="w-6 h-6 text-violet-400" />
          Multi-Agent Swarm
        </h2>
        <Button className="bg-violet-600 hover:bg-violet-700">
          <Plus className="w-4 h-4 mr-2" /> Create Swarm
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="rounded-xl p-4 bg-slate-900/50 border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-300 mb-3">Swarm Members</h3>
            <div className="space-y-2">
              {mockSwarm.agents.map((agent, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 border border-slate-800"
                >
                  <div>
                    <p className="text-sm font-medium text-white">{agent.name}</p>
                    <p className="text-xs text-slate-400 capitalize">{agent.role}</p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${agent.status === "active" ? "bg-emerald-400" : "bg-slate-500"}`} />
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 rounded-xl p-4 bg-slate-900/50 border border-slate-800 flex flex-col h-[500px]">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Swarm Execution</h3>
          <div className="flex-1 overflow-y-auto space-y-3 mb-4 p-2">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg ${msg.role === "user" ? "bg-blue-600/20 ml-auto max-w-[80%]" : "bg-slate-800/50 mr-auto max-w-[80%]"}`}
              >
                <p className="text-sm text-slate-200">{msg.content}</p>
              </motion.div>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Enter task for swarm..."
              className="bg-slate-900 border-slate-700"
              onKeyDown={(e) => e.key === "Enter" && executeTask()}
            />
            <Button onClick={executeTask} className="bg-blue-600 hover:bg-blue-700">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
