"use client";

import React, { useState, useEffect } from "react";
import {
  fetchTopology,
  fetchLogs,
  fetchAuditRecords,
  approveTier2Action,
} from "@/lib/api";
import {
  TopologyData,
  UserPersona,
  LogEvent,
  AuditRecord,
} from "@/lib/types";
import { Sidebar } from "@/components/sidebar";
import { Navbar } from "@/components/navbar";
import { DecisionCenter } from "@/components/decision-center";
import { LiveTelemetryFeed } from "@/components/live-telemetry-feed";
import { TopologyView } from "@/components/topology-view";

export default function Home() {
  const [topology, setTopology] = useState<TopologyData | null>(null);
  const [personas, setPersonas] = useState<UserPersona[]>([]);
  const [currentPersonaId, setCurrentPersonaId] = useState<string>("u_ciso");
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [auditRecords, setAuditRecords] = useState<AuditRecord[]>([]);
  const [activeTab, setActiveTab] = useState<"decisions" | "telemetry" | "topology">("decisions");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  // Load Initial Topology
  useEffect(() => {
    let active = true;
    fetchTopology()
      .then((topo) => {
        if (active) {
          setTopology(topo);
          if (topo.users && topo.users.length > 0) {
            setPersonas(topo.users);
          }
        }
      })
      .catch((err) => {
        console.error("Failed to load initial topology:", err);
      });

    return () => {
      active = false;
    };
  }, []);

  // Polling loop (every 1.5 seconds)
  useEffect(() => {
    let active = true;

    const executePoll = async () => {
      try {
        const [logsData, auditData] = await Promise.all([
          fetchLogs(100),
          fetchAuditRecords(currentPersonaId),
        ]);
        if (active) {
          setLogs(logsData.logs || []);
          setAuditRecords(auditData.records || []);
        }
      } catch (err) {
        console.error("Telemetry polling error:", err);
      }
    };

    const initialTimer = setTimeout(executePoll, 0);
    const interval = setInterval(executePoll, 1500);

    return () => {
      active = false;
      clearTimeout(initialTimer);
      clearInterval(interval);
    };
  }, [currentPersonaId]);

  // Persona change handler
  const handleSelectPersona = (newPersonaId: string) => {
    setCurrentPersonaId(newPersonaId);
  };

  // Full Refresh Handler
  const handleRefresh = async () => {
    try {
      const [topo, logsData, auditData] = await Promise.all([
        fetchTopology(),
        fetchLogs(100),
        fetchAuditRecords(currentPersonaId),
      ]);
      setTopology(topo);
      if (topo.users && topo.users.length > 0) {
        setPersonas(topo.users);
      }
      setLogs(logsData.logs || []);
      setAuditRecords(auditData.records || []);
    } catch (err) {
      console.error("Refresh error:", err);
    }
  };

  // Tier 2 1-Click Approval Handler
  const handleApprove = async (auditId: string) => {
    try {
      await approveTier2Action(auditId, currentPersonaId);
      const [logsData, auditData] = await Promise.all([
        fetchLogs(100),
        fetchAuditRecords(currentPersonaId),
      ]);
      setLogs(logsData.logs || []);
      setAuditRecords(auditData.records || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      alert(`Approval error: ${msg}`);
    }
  };

  const currentPersona = personas.find((p) => p.id === currentPersonaId) || {
    id: "u_ciso",
    name: "Elena Rostova",
    email: "elena.rostova@enterprise.internal",
    title: "Chief Information Security Officer (CISO)",
    role_category: "EXECUTIVE",
    department: "Information Security & Governance",
    asset_scope: "Enterprise Identity & Okta IAM",
    avatar_initials: "ER",
  };

  const pendingForMeCount = auditRecords.filter(
    (r) =>
      r.selected_tier === "TIER_2_DRAFTED_HITL" &&
      r.execution_status === "AWAITING_APPROVAL" &&
      (r.can_act || r.authorized_persona_id === currentPersonaId)
  ).length;

  const pageTitleMap = {
    decisions: "Autonomous Decision Center",
    telemetry: "Live Telemetry Feed",
    topology: "Enterprise Topology & Asset Scope",
  };

  return (
    <div className="min-h-screen flex bg-zinc-50/40 text-zinc-900">
      {/* TypeSafe-Style Fixed Left Sidebar with Bottom Account Switcher */}
      <Sidebar
        currentTab={activeTab}
        onSelectTab={setActiveTab}
        personas={personas}
        currentPersonaId={currentPersonaId}
        onSelectPersona={handleSelectPersona}
        pendingApprovalsForMeCount={pendingForMeCount}
        totalAuditsCount={auditRecords.length}
        totalLogsCount={topology?.total_logs_stored || logs.length}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          pageTitle={pageTitleMap[activeTab]}
          totalLogs={topology?.total_logs_stored || logs.length}
          totalAudits={auditRecords.length}
          onRefresh={handleRefresh}
        />

        <main className="flex-1 p-6 space-y-4 w-full max-w-[1600px] mx-auto">
          {activeTab === "decisions" && (
            <DecisionCenter
              records={auditRecords}
              currentPersona={currentPersona}
              allPersonas={personas}
              onApprove={handleApprove}
            />
          )}

          {activeTab === "telemetry" && (
            <LiveTelemetryFeed
              logs={logs}
              totalLogsStored={topology?.total_logs_stored || logs.length}
            />
          )}

          {activeTab === "topology" && (
            <TopologyView topology={topology} />
          )}
        </main>
      </div>
    </div>
  );
}
