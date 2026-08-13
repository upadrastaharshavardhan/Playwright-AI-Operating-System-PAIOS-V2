"use client";

import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const costData = [
  { name: "GPT-4o", cost: 450, tokens: 1200000 },
  { name: "Claude 3.5", cost: 320, tokens: 890000 },
  { name: "GPT-4o-mini", cost: 120, tokens: 2100000 },
  { name: "Local LLM", cost: 45, tokens: 3400000 },
];

const statusData = [
  { name: "Success", value: 94, color: "#10b981" },
  { name: "Failed", value: 4, color: "#ef4444" },
  { name: "Healed", value: 2, color: "#f59e0b" },
];

export function AnalyticsDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">ML Observability & Analytics</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800">
          <h3 className="text-lg font-semibold mb-4 text-slate-200">Cost by Model</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={costData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b" }} />
              <Bar dataKey="cost" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800">
          <h3 className="text-lg font-semibold mb-4 text-slate-200">Execution Outcomes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={statusData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b" }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-4">
            {statusData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-sm text-slate-300">{item.name}: {item.value}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
