"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

const generateData = () => Array.from({ length: 20 }, (_, i) => ({
  time: `${i}:00`,
  requests: Math.floor(Math.random() * 1000) + 500,
  latency: Math.floor(Math.random() * 200) + 50,
  errors: Math.floor(Math.random() * 20),
}));

export function RealTimeCharts() {
  const [data, setData] = useState(generateData());

  useEffect(() => {
    const interval = setInterval(() => setData(generateData()), 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800">
        <h3 className="text-lg font-semibold mb-4 text-slate-200">Request Throughput</h3>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorReq" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: "8px" }} itemStyle={{ color: "#e2e8f0" }} />
            <Area type="monotone" dataKey="requests" stroke="#3b82f6" fillOpacity={1} fill="url(#colorReq)" />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800">
        <h3 className="text-lg font-semibold mb-4 text-slate-200">Latency & Errors</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: "8px" }} itemStyle={{ color: "#e2e8f0" }} />
            <Line type="monotone" dataKey="latency" stroke="#8b5cf6" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="errors" stroke="#ef4444" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
}
