"use client";

import React from "react";
import { Zap, HandMetal, BookOpen, Activity } from "lucide-react";
import { AuditRecord } from "@/lib/types";

interface MetricsRibbonProps {
  totalLogs: number;
  records: AuditRecord[];
}

export function MetricsRibbon({ totalLogs, records }: MetricsRibbonProps) {
  const tier1Count = records.filter((r) => r.selected_tier === "TIER_1_AUTOMATED").length;
  const tier2Count = records.filter((r) => r.selected_tier === "TIER_2_DRAFTED_HITL").length;
  const tier2Pending = records.filter(
    (r) => r.selected_tier === "TIER_2_DRAFTED_HITL" && r.execution_status === "AWAITING_APPROVAL"
  ).length;
  const tier3Count = records.filter((r) => r.selected_tier === "TIER_3_PLAYBOOK").length;

  const totalAudits = records.length;
  const noiseFiltered = totalLogs > 0 ? Math.max(0, totalLogs - totalAudits) : 0;
  const filterRate = totalLogs > 0 ? ((noiseFiltered / totalLogs) * 100).toFixed(1) : "99.4";

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {/* Metric 1: Telemetry */}
      <div className="rounded-xl border border-zinc-200/80 bg-white p-3.5 flex items-center justify-between shadow-2xs">
        <div>
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Telemetry Lake
          </div>
          <div className="text-xl font-bold font-mono text-zinc-900 mt-0.5">
            {totalLogs.toLocaleString()}
          </div>
          <div className="text-[11px] text-zinc-400 mt-0.5">
            {filterRate}% noise filtered
          </div>
        </div>
        <div className="h-8 w-8 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-600">
          <Activity className="h-4 w-4" />
        </div>
      </div>

      {/* Metric 2: Tier 1 Autonomous */}
      <div className="rounded-xl border border-emerald-200/60 bg-emerald-50/30 p-3.5 flex items-center justify-between shadow-2xs">
        <div>
          <div className="text-[11px] font-medium text-emerald-700 uppercase tracking-wider font-mono">
            Tier 1: Autonomous
          </div>
          <div className="text-xl font-bold font-mono text-emerald-800 mt-0.5">
            {tier1Count}
          </div>
          <div className="text-[11px] text-emerald-600/80 mt-0.5">
            0ms automated mitigation
          </div>
        </div>
        <div className="h-8 w-8 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-700">
          <Zap className="h-4 w-4" />
        </div>
      </div>

      {/* Metric 3: Tier 2 HITL */}
      <div className="rounded-xl border border-amber-200/60 bg-amber-50/30 p-3.5 flex items-center justify-between shadow-2xs">
        <div>
          <div className="text-[11px] font-medium text-amber-700 uppercase tracking-wider font-mono">
            Tier 2: 1-Click HITL
          </div>
          <div className="text-xl font-bold font-mono text-amber-800 mt-0.5">
            {tier2Count}
          </div>
          <div className="text-[11px] text-amber-700/80 mt-0.5 font-medium">
            {tier2Pending > 0 ? `${tier2Pending} awaiting approval` : "All reconciled"}
          </div>
        </div>
        <div className="h-8 w-8 rounded-lg bg-amber-100 flex items-center justify-center text-amber-700">
          <HandMetal className="h-4 w-4" />
        </div>
      </div>

      {/* Metric 4: Tier 3 Playbooks */}
      <div className="rounded-xl border border-blue-200/60 bg-blue-50/30 p-3.5 flex items-center justify-between shadow-2xs">
        <div>
          <div className="text-[11px] font-medium text-blue-700 uppercase tracking-wider font-mono">
            Tier 3: Playbooks
          </div>
          <div className="text-xl font-bold font-mono text-blue-800 mt-0.5">
            {tier3Count}
          </div>
          <div className="text-[11px] text-blue-600/80 mt-0.5">
            High blast-radius actions
          </div>
        </div>
        <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700">
          <BookOpen className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
}
