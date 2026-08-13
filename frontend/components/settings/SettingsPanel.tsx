"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Settings, Key, Bell, Shield, Database } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function SettingsPanel() {
  const [healingEnabled, setHealingEnabled] = useState(true);
  const [threshold, setThreshold] = useState([75]);
  const [notifications, setNotifications] = useState(true);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <Settings className="w-6 h-6 text-slate-400" />
        Platform Settings
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-white">Self-Healing</h3>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Auto-Healing</p>
              <p className="text-xs text-slate-400">Automatically recover failed agents</p>
            </div>
            <Switch checked={healingEnabled} onCheckedChange={setHealingEnabled} />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-300">Health Threshold</span>
              <span className="text-blue-400">{threshold[0]}%</span>
            </div>
            <Slider value={threshold} onValueChange={setThreshold} max={100} step={5} />
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <Key className="w-5 h-5 text-violet-400" />
            <h3 className="font-semibold text-white">API Keys</h3>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-400">OpenAI API Key</label>
              <Input type="password" value="sk-••••••••••••••••••••••••••••••" className="bg-slate-900 border-slate-700 mt-1" readOnly />
            </div>
            <div>
              <label className="text-xs text-slate-400">Anthropic API Key</label>
              <Input type="password" value="sk-ant-•••••••••••••••••••••••••" className="bg-slate-900 border-slate-700 mt-1" readOnly />
            </div>
            <Button variant="outline" className="w-full border-slate-700 hover:bg-slate-800">Update Keys</Button>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="w-5 h-5 text-amber-400" />
            <h3 className="font-semibold text-white">Notifications</h3>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Alert Notifications</p>
              <p className="text-xs text-slate-400">Receive alerts via email/Slack</p>
            </div>
            <Switch checked={notifications} onCheckedChange={setNotifications} />
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="rounded-xl p-6 bg-slate-900/50 border border-slate-800 space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <Database className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-white">Infrastructure</h3>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-slate-300"><span>Neo4j Status</span><span className="text-emerald-400">Connected</span></div>
            <div className="flex justify-between text-slate-300"><span>Redis Status</span><span className="text-emerald-400">Connected</span></div>
            <div className="flex justify-between text-slate-300"><span>PostgreSQL</span><span className="text-emerald-400">Connected</span></div>
            <div className="flex justify-between text-slate-300"><span>Kafka</span><span className="text-emerald-400">Connected</span></div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
