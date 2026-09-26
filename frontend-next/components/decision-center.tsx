"use client";

import React, { useState } from "react";
import { AuditRecord, UserPersona, PERSONA_TIER_VISIBILITY } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import {
  Search,
  Inbox,
  Key,
  Lock,
  Copy,
  Check,
  Clock,
  ArrowUpRight,
} from "lucide-react";

interface DecisionCenterProps {
  records: AuditRecord[];
  currentPersona: UserPersona;
  allPersonas: UserPersona[];
  onApprove: (auditId: string) => Promise<void>;
}

export function DecisionCenter({
  records,
  currentPersona,
  allPersonas,
  onApprove,
}: DecisionCenterProps) {
  const [filterTab, setFilterTab] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [optimisticApproved, setOptimisticApproved] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  // Determine tiers visible to this persona (Data Drives the UI)
  const visibleTiers = PERSONA_TIER_VISIBILITY[currentPersona.id] || [
    "TIER_1_AUTOMATED",
    "TIER_2_DRAFTED_HITL",
    "TIER_3_PLAYBOOK",
  ];

  // Strictly filter by this persona's visibility scope
  const personaVisibleRecords = records.filter((r) =>
    visibleTiers.includes(r.selected_tier)
  );

  const pendingForMe = personaVisibleRecords.filter(
    (r) =>
      r.selected_tier === "TIER_2_DRAFTED_HITL" &&
      r.execution_status === "AWAITING_APPROVAL" &&
      !optimisticApproved.has(r.id) &&
      (r.can_act || r.authorized_persona_id === currentPersona.id)
  );

  const tier1Records = personaVisibleRecords.filter(
    (r) => r.selected_tier === "TIER_1_AUTOMATED"
  );
  const tier2Records = personaVisibleRecords.filter(
    (r) => r.selected_tier === "TIER_2_DRAFTED_HITL"
  );
  const tier3Records = personaVisibleRecords.filter(
    (r) => r.selected_tier === "TIER_3_PLAYBOOK"
  );

  const getFilteredByTab = () => {
    switch (filterTab) {
      case "pending":
        return pendingForMe;
      case "tier1":
        return tier1Records;
      case "tier2":
        return tier2Records;
      case "tier3":
        return tier3Records;
      default:
        return personaVisibleRecords;
    }
  };

  const filtered = getFilteredByTab().filter((record) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      record.attack_class.toLowerCase().includes(query) ||
      record.target_user_id.toLowerCase().includes(query) ||
      record.target_service.toLowerCase().includes(query) ||
      record.reason.toLowerCase().includes(query)
    );
  });

  // Selected record for right activity panel
  const activeRecord =
    filtered.find((r) => r.id === selectedIncidentId) ||
    filtered.find((r) => r.execution_status === "AWAITING_APPROVAL") ||
    filtered[0] ||
    null;

  const handleApprove = async (auditId: string) => {
    setOptimisticApproved((prev) => new Set(prev).add(auditId));
    try {
      await onApprove(auditId);
    } catch {
      setOptimisticApproved((prev) => {
        const next = new Set(prev);
        next.delete(auditId);
        return next;
      });
    }
  };

  const handleCopy = (text: string, isCmd: boolean = false) => {
    navigator.clipboard.writeText(text);
    if (isCmd) {
      setCopiedCmd(text);
      setTimeout(() => setCopiedCmd(null), 1500);
    } else {
      setCopiedId(text);
      setTimeout(() => setCopiedId(null), 1500);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 select-none items-start">
      {/* LEFT COLUMN: Main Table (~65% width) */}
      <div className="lg:col-span-8 space-y-3.5">
        {/* Header Block */}
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Lock className="h-3 w-3" />
            <span>Governance Database</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-900">
            Incident & Threat Governance
          </h1>
          <p className="text-xs text-zinc-500">
            Automated detection, blast radius containment, and role-gated 1-click execution.
          </p>
        </div>

        {/* View Tabs (shadcn Tabs Primitive) + Search Box */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-200/80 pb-2">
          <Tabs
            value={filterTab}
            onValueChange={(val) => setFilterTab(val as string)}
            className="w-full sm:w-auto"
          >
            <TabsList className="bg-zinc-100/90 border border-zinc-200/70 p-0.5 h-8">
              <TabsTrigger value="all" className="text-xs px-2.5 py-1">
                All Visible ({personaVisibleRecords.length})
              </TabsTrigger>

              {visibleTiers.includes("TIER_2_DRAFTED_HITL") && (
                <TabsTrigger
                  value="pending"
                  className="text-xs px-2.5 py-1 gap-1 text-amber-800 data-active:text-amber-900"
                >
                  <Key className="h-3 w-3 text-amber-700" />
                  <span>Pending ({pendingForMe.length})</span>
                </TabsTrigger>
              )}

              {visibleTiers.includes("TIER_1_AUTOMATED") && (
                <TabsTrigger value="tier1" className="text-xs px-2.5 py-1">
                  Tier 1 Auto ({tier1Records.length})
                </TabsTrigger>
              )}

              {visibleTiers.includes("TIER_2_DRAFTED_HITL") && (
                <TabsTrigger value="tier2" className="text-xs px-2.5 py-1">
                  Tier 2: 1-Click ({tier2Records.length})
                </TabsTrigger>
              )}

              {visibleTiers.includes("TIER_3_PLAYBOOK") && (
                <TabsTrigger value="tier3" className="text-xs px-2.5 py-1">
                  Tier 3 Playbooks ({tier3Records.length})
                </TabsTrigger>
              )}
            </TabsList>
          </Tabs>

          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-zinc-400" />
            <input
              type="text"
              placeholder="Search incidents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 rounded-md border border-zinc-200 bg-white pl-8 pr-2.5 text-xs text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400 focus:outline-none w-48 shadow-2xs"
            />
          </div>
        </div>

        {/* Table Container - Strictly table-fixed with proportional widths for ZERO SCROLL */}
        <div className="rounded-xl border border-zinc-200/90 bg-white overflow-hidden shadow-2xs">
          <Table className="w-full table-fixed">
            <TableHeader className="bg-zinc-50/80 border-b border-zinc-200">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[32%] text-[11px] font-medium text-zinc-500">Incident & Vector</TableHead>
                <TableHead className="w-[22%] text-[11px] font-medium text-zinc-500">Target Identity</TableHead>
                <TableHead className="w-[16%] text-[11px] font-medium text-zinc-500">Tier</TableHead>
                <TableHead className="w-[10%] text-[11px] font-medium text-zinc-500 text-right">Threat %</TableHead>
                <TableHead className="w-[10%] text-[11px] font-medium text-zinc-500 text-right">Blast %</TableHead>
                <TableHead className="w-[10%] text-[11px] font-medium text-zinc-500 text-right">Resolution</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-40 text-center text-xs text-zinc-400">
                    <div className="h-8 w-8 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-400 mx-auto mb-2">
                      <Inbox className="h-4 w-4" />
                    </div>
                    <div>No incidents match this view for {currentPersona.name}.</div>
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((record) => {
                  const isSelected = activeRecord?.id === record.id;
                  const payload = record.action_payload || {};
                  const isTier1 = record.selected_tier === "TIER_1_AUTOMATED";
                  const isTier2 = record.selected_tier === "TIER_2_DRAFTED_HITL";
                  const isTier3 = record.selected_tier === "TIER_3_PLAYBOOK";

                  const isOptimisticallyApproved = optimisticApproved.has(record.id);
                  const isExecuted =
                    isOptimisticallyApproved ||
                    record.execution_status === "EXECUTED" ||
                    record.execution_status === "EXECUTED_BY_OPERATOR";

                  const authorizedPersona = allPersonas.find(
                    (p) => p.id === (record.authorized_persona_id || payload.authorized_persona_id)
                  );
                  const canAct = record.can_act ?? (record.authorized_persona_id === currentPersona.id);

                  const rowShadeClass = isExecuted
                    ? "bg-zinc-50/40 text-zinc-500 opacity-80"
                    : "bg-white text-zinc-900";

                  const shortId = `SEC-${record.id.slice(4, 9).toUpperCase()}`;

                  return (
                    <TableRow
                      key={record.id}
                      className={`text-xs border-b border-zinc-100 hover:bg-zinc-50/90 transition-all cursor-pointer group ${rowShadeClass} ${
                        isSelected ? "bg-zinc-100/60 font-medium" : ""
                      }`}
                      onClick={() => setSelectedIncidentId(record.id)}
                    >
                      {/* Column 1: Incident & Vector */}
                      <TableCell className="overflow-hidden">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-[10px] text-zinc-400">{shortId}</span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCopy(record.id, false);
                            }}
                            className="opacity-0 group-hover:opacity-100 text-zinc-400 hover:text-zinc-700 transition-opacity"
                            title="Copy full incident ID"
                          >
                            {copiedId === record.id ? (
                              <Check className="h-3 w-3 text-emerald-600" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </button>
                        </div>
                        <div className="font-semibold text-zinc-900 font-mono text-[11px] tracking-tight truncate">
                          {record.attack_class}
                        </div>
                        <div className="text-[10px] text-zinc-400 font-mono">
                          {record.timestamp.includes("T") ? record.timestamp.split("T")[1].slice(0, 8) : record.timestamp}
                        </div>
                      </TableCell>

                      {/* Column 2: Target Identity */}
                      <TableCell className="overflow-hidden">
                        <div className="flex items-center gap-1.5">
                          <div className="h-5 w-5 rounded-full bg-zinc-100 text-zinc-700 border border-zinc-200 font-mono text-[9px] flex items-center justify-center shrink-0">
                            {record.target_user_id.slice(2, 4).toUpperCase()}
                          </div>
                          <div className="truncate">
                            <div className="font-medium text-zinc-800 text-[11px] truncate">
                              {record.target_user_id}
                            </div>
                            <div className="text-[10px] text-zinc-400 truncate">
                              {record.target_service}
                            </div>
                          </div>
                        </div>
                      </TableCell>

                      {/* Column 3: Tier */}
                      <TableCell className="overflow-hidden">
                        {isTier1 && (
                          <Badge variant="outline" className="gap-1 bg-emerald-50/60 text-emerald-700 border-emerald-200 font-mono text-[10px] px-1.5 py-0.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                            Tier 1
                          </Badge>
                        )}
                        {isTier2 && (
                          <Badge variant="outline" className="gap-1 bg-amber-50/60 text-amber-800 border-amber-200 font-mono text-[10px] px-1.5 py-0.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                            Tier 2
                          </Badge>
                        )}
                        {isTier3 && (
                          <Badge variant="outline" className="gap-1 bg-blue-50/60 text-blue-700 border-blue-200 font-mono text-[10px] px-1.5 py-0.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                            Tier 3
                          </Badge>
                        )}
                      </TableCell>

                      {/* Column 4: Threat % */}
                      <TableCell className="text-right font-mono">
                        <span className={record.threat_confidence > 0.7 ? "font-bold text-red-600" : "text-zinc-700"}>
                          {(record.threat_confidence * 100).toFixed(0)}%
                        </span>
                      </TableCell>

                      {/* Column 5: Blast % */}
                      <TableCell className="text-right font-mono">
                        <span className={record.blast_radius > 0.4 ? "font-bold text-amber-700" : "text-zinc-700"}>
                          {(record.blast_radius * 100).toFixed(0)}%
                        </span>
                      </TableCell>

                      {/* Column 6: Resolution / Action */}
                      <TableCell className="text-right overflow-hidden" onClick={(e) => e.stopPropagation()}>
                        {isExecuted ? (
                          <Badge variant="secondary" className="gap-1 bg-emerald-50 text-emerald-700 border-emerald-200 font-mono text-[10px]">
                            <Check className="h-3 w-3" />
                            Mitigated
                          </Badge>
                        ) : isTier1 ? (
                          <span className="text-[10px] font-mono text-zinc-400">
                            Auto-WAF
                          </span>
                        ) : isTier2 ? (
                          canAct ? (
                            <Button
                              size="sm"
                              onClick={() => handleApprove(record.id)}
                              className="h-6.5 text-[11px] font-medium px-2 shadow-2xs transition-all active:scale-95"
                            >
                              Authorize
                            </Button>
                          ) : (
                            <Tooltip>
                              <TooltipTrigger>
                                <span className="inline-flex items-center text-[10px] text-zinc-400 border border-zinc-200 bg-zinc-50 px-1.5 py-0.5 rounded cursor-not-allowed gap-1 font-mono">
                                  <Lock className="h-2.5 w-2.5" />
                                  <span>{authorizedPersona?.title.split("(")[0].trim() || "CISO"}</span>
                                </span>
                              </TooltipTrigger>
                              <TooltipContent className="text-xs bg-zinc-800 text-white max-w-xs">
                                Authority: Only {authorizedPersona?.name} holds execution authority for this asset scope.
                              </TooltipContent>
                            </Tooltip>
                          )
                        ) : (
                          <span className="text-[11px] font-mono text-blue-700 font-medium flex items-center justify-end gap-1">
                            <span>Playbook</span>
                            <ArrowUpRight className="h-3 w-3" />
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* RIGHT COLUMN: Incident Activity & Mitigation Timeline (~35% width) */}
      <div className="lg:col-span-4 space-y-3.5">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Clock className="h-3 w-3" />
            <span>Real-Time Audit Stream</span>
          </div>
          <h2 className="text-base font-bold tracking-tight text-zinc-900">
            Incident Activity & Timeline
          </h2>
          <p className="text-xs text-zinc-500">
            Live containment actions and leadership sign-off audit records.
          </p>
        </div>

        {/* Informational Alert Banner */}
        {pendingForMe.length > 0 && (
          <div className="rounded-lg bg-amber-50/70 border border-amber-200/80 p-2.5 text-xs text-amber-900 space-y-1">
            <div className="font-semibold flex items-center gap-1.5">
              <Key className="h-3.5 w-3.5 text-amber-700" />
              <span>{pendingForMe.length} Pending Governance Action{pendingForMe.length > 1 ? "s" : ""}</span>
            </div>
            <p className="text-[11px] text-amber-800 leading-snug">
              Perimeter subnets are awaiting your 1-click authorization to enforce containment.
            </p>
          </div>
        )}

        {/* Selected Incident Detail Card (shadcn Card Primitive) */}
        {activeRecord && (
          <Card className="p-0 border-zinc-200/90 bg-white shadow-2xs">
            <CardHeader className="p-3.5 pb-2.5 border-b border-zinc-100 flex flex-row items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                <CardTitle className="font-semibold text-xs font-mono text-zinc-900">
                  {activeRecord.attack_class}
                </CardTitle>
              </div>
              <span className="text-[10px] font-mono text-zinc-400">
                SEC-{activeRecord.id.slice(4, 9).toUpperCase()}
              </span>
            </CardHeader>

            <CardContent className="p-3.5 space-y-2.5 text-xs">
              {/* Target & Assigned Person */}
              <div className="flex items-center justify-between py-1 border-b border-zinc-100/70 text-[11px]">
                <span className="text-zinc-500">Target User:</span>
                <span className="font-medium text-zinc-800 font-mono">{activeRecord.target_user_id}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-zinc-100/70 text-[11px]">
                <span className="text-zinc-500">Service Asset:</span>
                <span className="font-medium text-zinc-800 font-mono">{activeRecord.target_service}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-zinc-100/70 text-[11px]">
                <span className="text-zinc-500">Threat / Blast:</span>
                <span className="font-mono text-zinc-800">
                  {(activeRecord.threat_confidence * 100).toFixed(0)}% Threat • {(activeRecord.blast_radius * 100).toFixed(0)}% Blast
                </span>
              </div>

              {/* Rationale & Guardrail */}
              <div className="bg-zinc-50 rounded-lg p-2.5 text-zinc-700 text-[11px] leading-relaxed border border-zinc-200/60">
                <strong className="text-zinc-900 block mb-0.5">Decision Rationale:</strong>
                {activeRecord.reason}
              </div>

              {activeRecord.action_payload?.blast_radius_guardrail && (
                <div className="bg-amber-50/60 rounded-lg p-2 text-amber-900 text-[11px] border border-amber-200/60">
                  <strong>Guardrail: </strong>
                  {activeRecord.action_payload.blast_radius_guardrail}
                </div>
              )}

              {/* Action Button inside Timeline Card */}
              {activeRecord.selected_tier === "TIER_2_DRAFTED_HITL" && (
                <div className="pt-2">
                  {optimisticApproved.has(activeRecord.id) ||
                  activeRecord.execution_status === "EXECUTED_BY_OPERATOR" ? (
                    <div className="w-full text-center py-2 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-medium border border-emerald-200 flex items-center justify-center gap-1.5">
                      <Check className="h-4 w-4" />
                      <span>Mitigation Authorized & Executed</span>
                    </div>
                  ) : activeRecord.can_act || activeRecord.authorized_persona_id === currentPersona.id ? (
                    <Button
                      onClick={() => handleApprove(activeRecord.id)}
                      className="w-full h-8 text-xs font-medium shadow-2xs transition-all active:scale-98"
                    >
                      Authorize 1-Click Mitigation
                    </Button>
                  ) : (
                    <div className="w-full text-center py-2 rounded-lg bg-zinc-50 text-zinc-500 text-xs border border-zinc-200 flex items-center justify-center gap-1.5">
                      <Lock className="h-3.5 w-3.5 text-zinc-400" />
                      <span>Requires {allPersonas.find((p) => p.id === activeRecord.authorized_persona_id)?.name || "CISO"} Authorization</span>
                    </div>
                  )}
                </div>
              )}

              {/* Tier 3 Technical Playbook in Timeline Card */}
              {activeRecord.selected_tier === "TIER_3_PLAYBOOK" && (
                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400 font-mono">
                    Mitigation Procedures:
                  </div>
                  <div className="space-y-1 text-[11px] font-mono">
                    {(activeRecord.action_payload?.technical_steps || [
                      "1. Isolate compromised worker nodes from service mesh",
                      "2. Invalidate leaked AWS IAM temporary credentials & rotate KMS master keys",
                      "3. Re-route live traffic through emergency backup cluster",
                      "4. Conduct forensic audit on container runtime memory dumps",
                    ]).map((step: string, idx: number) => (
                      <div key={idx} className="p-1.5 rounded bg-zinc-50 border border-zinc-100 text-zinc-800 text-[10px]">
                        {step}
                      </div>
                    ))}
                  </div>

                  {activeRecord.action_payload?.verification_command && (
                    <div className="rounded bg-zinc-100 border border-zinc-200 p-2 font-mono text-[11px] text-zinc-800 flex items-center justify-between gap-1.5 mt-2">
                      <div className="truncate">
                        <span className="text-zinc-900 select-all">{activeRecord.action_payload.verification_command}</span>
                      </div>
                      <button
                        onClick={() => handleCopy(activeRecord.action_payload?.verification_command || "", true)}
                        className="text-zinc-400 hover:text-zinc-700 shrink-0 p-1"
                        title="Copy command"
                      >
                        {copiedCmd === activeRecord.action_payload.verification_command ? (
                          <Check className="h-3 w-3 text-emerald-600" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Activity Feed Summary List */}
        <div className="space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400 font-mono">
            Recent Mitigation Timeline
          </div>
          <div className="space-y-2">
            {personaVisibleRecords.slice(0, 5).map((r) => {
              const isExec = optimisticApproved.has(r.id) || r.execution_status.includes("EXECUTED");
              const isPend = !isExec && r.execution_status === "AWAITING_APPROVAL";
              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedIncidentId(r.id)}
                  className={`p-2.5 rounded-lg border transition-all cursor-pointer text-xs ${
                    activeRecord?.id === r.id
                      ? "border-zinc-300 bg-white shadow-2xs"
                      : "border-zinc-200/70 bg-white/70 hover:bg-white"
                  }`}
                >
                  <div className="flex items-center justify-between font-mono text-[10px]">
                    <span className="text-zinc-800 font-semibold">{r.attack_class}</span>
                    <span className="text-zinc-400">
                      {r.timestamp.includes("T") ? r.timestamp.split("T")[1].slice(0, 8) : r.timestamp}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mt-1 text-[11px]">
                    <span className="text-zinc-500 font-mono">{r.target_user_id}</span>
                    {isPend && (
                      <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-medium">
                        Action Required
                      </span>
                    )}
                    {isExec && (
                      <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 font-medium">
                        Mitigated
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
