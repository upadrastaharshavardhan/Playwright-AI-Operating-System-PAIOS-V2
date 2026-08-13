"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { RealTimeCharts } from "@/components/dashboard/RealTimeCharts";
import { AgentMonitor } from "@/components/agents/AgentMonitor";
import { AnalyticsDashboard } from "@/components/analytics/AnalyticsDashboard";
import { AlertTimeline } from "@/components/monitoring/AlertTimeline";
import { HealingStatus } from "@/components/self-healing/HealingStatus";
import { SettingsPanel } from "@/components/settings/SettingsPanel";
import { SwarmControl } from "@/components/agents/SwarmControl";

export default function Home() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <DashboardHeader />
      <main className="container mx-auto px-4 py-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-slate-900 border border-slate-800 p-1 flex flex-wrap gap-1">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="agents">Agents</TabsTrigger>
              <TabsTrigger value="swarm">Swarm</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
              <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
              <TabsTrigger value="healing">Self-Healing</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <AnimatePresence mode="wait">
              <TabsContent value="overview" className="space-y-6">
                <StatsCards />
                <RealTimeCharts />
              </TabsContent>
              <TabsContent value="agents"><AgentMonitor /></TabsContent>
              <TabsContent value="swarm"><SwarmControl /></TabsContent>
              <TabsContent value="analytics"><AnalyticsDashboard /></TabsContent>
              <TabsContent value="monitoring"><AlertTimeline /></TabsContent>
              <TabsContent value="healing"><HealingStatus /></TabsContent>
              <TabsContent value="settings"><SettingsPanel /></TabsContent>
            </AnimatePresence>
          </Tabs>
        </motion.div>
      </main>
    </div>
  );
}
