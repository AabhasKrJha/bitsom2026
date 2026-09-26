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
  ArrowUpRight,
  SlidersHorizontal,
} from "lucide-react";

interface DecisionCenterProps {
  records: AuditRecord[];
  currentPersona: UserPersona;
  allPersonas: UserPersona[];
  onApprove: (auditId: string) => Promise<void>;
}

function getShortRole(persona?: UserPersona) {
  if (!persona) return "Authority";
  if (persona.id === "u_ciso") return "CISO";
  if (persona.id === "u_cto") return "CTO";
  if (persona.id === "u_devops") return "DevOps";
  if (persona.id === "u_eng") return "Eng Lead";
  if (persona.id === "u_soc") return "SOC";
  return persona.name.split(" ")[0];
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

  // Strictly filter by this persona's visibility scope & role authority
  const personaVisibleRecords = records.filter((r) => {
    // 1. Must be in this persona's visible tiers
    if (!visibleTiers.includes(r.selected_tier)) return false;

    // 2. SOC persona has organization-wide oversight across all fleets & tiers
    if (currentPersona.id === "u_soc") return true;

    // 3. Other personas strictly see incidents in their asset scope or authority
    return (
      r.authorized_persona_id === currentPersona.id ||
      r.target_user_id === currentPersona.id ||
      r.action_payload?.authorized_persona_id === currentPersona.id
    );
  });

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
    const targetPersona = allPersonas.find((p) => p.id === record.target_user_id);
    return (
      record.attack_class.toLowerCase().includes(query) ||
      record.target_user_id.toLowerCase().includes(query) ||
      (targetPersona && targetPersona.name.toLowerCase().includes(query)) ||
      record.target_service.toLowerCase().includes(query) ||
      record.reason.toLowerCase().includes(query)
    );
  });

  // Selected record for right inspector panel
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

  const activeTargetPersona = activeRecord
    ? allPersonas.find((p) => p.id === activeRecord.target_user_id)
    : null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 select-none items-start">
      {/* LEFT COLUMN: Main Table (~65% width) */}
      <div className="lg:col-span-8 space-y-3">
        {/* Sleek, Compact Toolbar (View Tabs + Search) */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
          <Tabs
            value={filterTab}
            onValueChange={(val) => setFilterTab(val as string)}
            className="w-full sm:w-auto"
          >
            <TabsList className="bg-zinc-100/90 border border-zinc-200/80 p-0.5 h-8">
              <TabsTrigger value="all" className="text-xs px-2.5 py-1">
                All ({personaVisibleRecords.length})
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
                  Tier 1 ({tier1Records.length})
                </TabsTrigger>
              )}

              {visibleTiers.includes("TIER_2_DRAFTED_HITL") && (
                <TabsTrigger value="tier2" className="text-xs px-2.5 py-1">
                  Tier 2 ({tier2Records.length})
                </TabsTrigger>
              )}

              {visibleTiers.includes("TIER_3_PLAYBOOK") && (
                <TabsTrigger value="tier3" className="text-xs px-2.5 py-1">
                  Tier 3 ({tier3Records.length})
                </TabsTrigger>
              )}
            </TabsList>
          </Tabs>

          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-400" />
            <input
              type="text"
              placeholder="Filter incidents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 rounded-lg border border-zinc-200 bg-white pl-8 pr-2.5 text-xs text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400 focus:outline-none w-52 shadow-2xs"
            />
          </div>
        </div>

        {/* Table Container - table-fixed with zero text wrapping */}
        <div className="rounded-xl border border-zinc-200/90 bg-white shadow-2xs overflow-clip">
          <Table className="w-full table-fixed">
            <TableHeader className="bg-zinc-50/95 backdrop-blur-xs border-b border-zinc-200 sticky top-14 z-10 shadow-2xs">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[32%] text-[11px] font-medium text-zinc-500">Incident Vector</TableHead>
                <TableHead className="w-[20%] text-[11px] font-medium text-zinc-500">Target</TableHead>
                <TableHead className="w-[12%] text-[11px] font-medium text-zinc-500">Tier</TableHead>
                <TableHead className="w-[8%] text-[11px] font-medium text-zinc-500 text-right">Threat</TableHead>
                <TableHead className="w-[8%] text-[11px] font-medium text-zinc-500 text-right">Blast</TableHead>
                <TableHead className="w-[9%] text-[11px] font-medium text-zinc-500 text-right">Time</TableHead>
                <TableHead className="w-[11%] text-[11px] font-medium text-zinc-500 text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-40 text-center text-xs text-zinc-400">
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

                  const isOptimisticallyApproved = optimisticApproved.has(record.id);
                  const isExecuted =
                    isOptimisticallyApproved ||
                    record.execution_status === "EXECUTED" ||
                    record.execution_status === "EXECUTED_BY_OPERATOR";

                  const authorizedPersona = allPersonas.find(
                    (p) => p.id === (record.authorized_persona_id || payload.authorized_persona_id)
                  );
                  const canAct = record.can_act ?? (record.authorized_persona_id === currentPersona.id);

                  const targetPersona = allPersonas.find((p) => p.id === record.target_user_id);
                  const initials = targetPersona?.avatar_initials || (record.target_user_id.startsWith("u_") ? record.target_user_id.slice(2, 4).toUpperCase() : "ID");
                  const displayName = targetPersona?.name || record.target_user_id;

                  const rowShadeClass = isExecuted
                    ? "bg-zinc-50/40 text-zinc-500 opacity-80"
                    : "bg-white text-zinc-900";

                  const shortId = `SEC-${record.id.slice(4, 9).toUpperCase()}`;
                  const timeFormatted = record.timestamp.includes("T")
                    ? record.timestamp.split("T")[1].slice(0, 8)
                    : record.timestamp.includes(" ")
                    ? record.timestamp.split(" ")[1]
                    : record.timestamp;

                  return (
                    <TableRow
                      key={record.id}
                      className={`text-xs border-b border-zinc-100 hover:bg-zinc-50/90 transition-all cursor-pointer group ${rowShadeClass} ${
                        isSelected ? "bg-zinc-100/70 font-medium" : ""
                      }`}
                      onClick={() => setSelectedIncidentId(record.id)}
                    >
                      {/* Column 1: Incident Vector (Single line) */}
                      <TableCell className="overflow-hidden py-2 whitespace-nowrap">
                        <div className="flex items-center gap-1.5 truncate">
                          <span className="font-mono text-[10px] text-zinc-400 shrink-0">{shortId}</span>
                          <span className="font-semibold text-zinc-900 text-xs truncate">{record.attack_class}</span>
                        </div>
                      </TableCell>

                      {/* Column 2: Target (Single line) */}
                      <TableCell className="overflow-hidden py-2 whitespace-nowrap">
                        <div className="flex items-center gap-1.5 truncate">
                          <div className="h-5 w-5 rounded-full bg-zinc-100 text-zinc-700 border border-zinc-200 font-mono text-[9px] font-medium flex items-center justify-center shrink-0">
                            {initials}
                          </div>
                          <span className="font-medium text-zinc-800 text-xs truncate">{displayName}</span>
                        </div>
                      </TableCell>

                      {/* Column 3: Tier */}
                      <TableCell className="overflow-hidden py-2 whitespace-nowrap">
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
                        {record.selected_tier === "TIER_3_PLAYBOOK" && (
                          <Badge variant="outline" className="gap-1 bg-blue-50/60 text-blue-700 border-blue-200 font-mono text-[10px] px-1.5 py-0.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                            Tier 3
                          </Badge>
                        )}
                      </TableCell>

                      {/* Column 4: Threat % */}
                      <TableCell className="text-right font-mono py-2 whitespace-nowrap text-xs">
                        <span className={record.threat_confidence > 0.7 ? "font-bold text-red-600" : "text-zinc-700"}>
                          {(record.threat_confidence * 100).toFixed(0)}%
                        </span>
                      </TableCell>

                      {/* Column 5: Blast % */}
                      <TableCell className="text-right font-mono py-2 whitespace-nowrap text-xs">
                        <span className={record.blast_radius > 0.4 ? "font-bold text-amber-700" : "text-zinc-700"}>
                          {(record.blast_radius * 100).toFixed(0)}%
                        </span>
                      </TableCell>

                      {/* Column 6: Time */}
                      <TableCell className="text-right font-mono text-[11px] text-zinc-400 py-2 whitespace-nowrap">
                        {timeFormatted}
                      </TableCell>

                      {/* Column 7: Resolution / Action */}
                      <TableCell className="text-right overflow-hidden py-2 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                        {isExecuted ? (
                          <Badge variant="secondary" className="gap-1 bg-emerald-50 text-emerald-700 border-emerald-200 font-mono text-[10px] px-1.5 py-0.5">
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
                              size="xs"
                              variant="outline"
                              onClick={() => handleApprove(record.id)}
                              className="h-6 text-[11px] font-medium px-2 bg-white hover:bg-zinc-100 text-zinc-900 border-zinc-200 shadow-2xs"
                            >
                              Authorize
                            </Button>
                          ) : (
                            <Tooltip>
                              <TooltipTrigger>
                                <span className="inline-flex items-center text-[10px] text-zinc-600 border border-zinc-200 bg-zinc-50 px-1.5 py-0.5 rounded cursor-not-allowed gap-1 font-mono font-medium">
                                  <Lock className="h-2.5 w-2.5 text-zinc-400" />
                                  <span>{getShortRole(authorizedPersona)}</span>
                                </span>
                              </TooltipTrigger>
                              <TooltipContent className="text-xs bg-zinc-800 text-white max-w-xs">
                                Requires {authorizedPersona?.name || "Executive"} sign-off
                              </TooltipContent>
                            </Tooltip>
                          )
                        ) : (
                          <span className="text-[11px] font-mono text-blue-700 font-medium inline-flex items-center gap-0.5">
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

      {/* RIGHT COLUMN: Streamlined Incident Inspector (~35% width, Sticky) */}
      <div className="lg:col-span-4 sticky top-20 self-start space-y-2">
        <div className="flex items-center justify-between text-xs font-medium text-zinc-500 px-0.5">
          <span className="flex items-center gap-1.5">
            <SlidersHorizontal className="h-3.5 w-3.5 text-zinc-400" />
            <span>Incident Inspector</span>
          </span>
          {activeRecord && (
            <div className="flex items-center gap-1 font-mono text-[10px] text-zinc-400">
              <span>SEC-{activeRecord.id.slice(4, 9).toUpperCase()}</span>
              <button
                onClick={() => handleCopy(activeRecord.id, false)}
                className="hover:text-zinc-700 p-0.5 rounded"
                title="Copy incident ID"
              >
                {copiedId === activeRecord.id ? (
                  <Check className="h-2.5 w-2.5 text-emerald-600" />
                ) : (
                  <Copy className="h-2.5 w-2.5" />
                )}
              </button>
            </div>
          )}
        </div>

        {/* Selected Incident Detail Card */}
        {activeRecord ? (
          <Card className="p-0 border-zinc-200/90 bg-white shadow-2xs">
            <CardHeader className="p-3 pb-2 border-b border-zinc-100 flex flex-row items-center justify-between">
              <div className="flex items-center gap-2 overflow-hidden">
                <span
                  className={`h-2 w-2 rounded-full shrink-0 ${
                    activeRecord.selected_tier === "TIER_1_AUTOMATED"
                      ? "bg-emerald-500"
                      : activeRecord.selected_tier === "TIER_2_DRAFTED_HITL"
                      ? "bg-amber-500"
                      : "bg-blue-500"
                  }`}
                />
                <CardTitle className="font-semibold text-xs text-zinc-900 truncate">
                  {activeRecord.attack_class}
                </CardTitle>
              </div>

              {activeRecord.selected_tier === "TIER_1_AUTOMATED" && (
                <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px] font-mono">
                  Tier 1
                </Badge>
              )}
              {activeRecord.selected_tier === "TIER_2_DRAFTED_HITL" && (
                <Badge variant="outline" className="bg-amber-50 text-amber-800 border-amber-200 text-[10px] font-mono">
                  Tier 2
                </Badge>
              )}
              {activeRecord.selected_tier === "TIER_3_PLAYBOOK" && (
                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-[10px] font-mono">
                  Tier 3
                </Badge>
              )}
            </CardHeader>

            <CardContent className="p-3 space-y-2 text-xs">
              {/* Target & Assigned Person */}
              <div className="flex items-center justify-between py-1 border-b border-zinc-100 text-[11px]">
                <span className="text-zinc-500">Target:</span>
                <span className="font-medium text-zinc-800">
                  {activeTargetPersona ? activeTargetPersona.name : activeRecord.target_user_id}
                </span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-zinc-100 text-[11px]">
                <span className="text-zinc-500">Asset:</span>
                <span className="font-medium text-zinc-800 font-mono text-[10px] truncate max-w-[200px]">
                  {activeRecord.target_service}
                </span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-zinc-100 text-[11px]">
                <span className="text-zinc-500">Risk Profile:</span>
                <span className="font-mono text-zinc-800 text-[11px]">
                  {(activeRecord.threat_confidence * 100).toFixed(0)}% Threat • {(activeRecord.blast_radius * 100).toFixed(0)}% Blast
                </span>
              </div>

              {/* Rationale & Guardrail */}
              <div className="bg-zinc-50 rounded-lg p-2.5 text-zinc-700 text-[11px] leading-relaxed border border-zinc-200/60">
                {activeRecord.reason}
              </div>

              {activeRecord.action_payload?.blast_radius_guardrail && (
                <div className="bg-amber-50/60 rounded-lg p-2 text-amber-900 text-[11px] border border-amber-200/60">
                  <span className="font-semibold">Guardrail: </span>
                  {activeRecord.action_payload.blast_radius_guardrail}
                </div>
              )}

              {/* Tier 1 Machine Autonomous Enforcement Receipt */}
              {activeRecord.selected_tier === "TIER_1_AUTOMATED" && (
                <div className="p-2 rounded-lg bg-zinc-50 border border-zinc-200/60 text-[11px] font-mono space-y-1">
                  <div className="flex justify-between text-zinc-600">
                    <span>Rule:</span>
                    <span className="text-zinc-900 font-semibold">{activeRecord.action_payload?.execution_receipt?.rule_id || `AUTO-${activeRecord.id.slice(4, 9).toUpperCase()}`}</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Enforcement:</span>
                    <span className="text-zinc-900">{activeRecord.action_payload?.execution_receipt?.enforcement_point || "Edge WAF"}</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Status:</span>
                    <span className="text-emerald-700 font-semibold flex items-center gap-1">
                      <Check className="h-3 w-3" /> Auto-Enforced
                    </span>
                  </div>
                </div>
              )}

              {/* Tier 2 HITL 1-Click Mitigation Action */}
              {activeRecord.selected_tier === "TIER_2_DRAFTED_HITL" && (
                <div className="pt-1">
                  {optimisticApproved.has(activeRecord.id) ||
                  activeRecord.execution_status === "EXECUTED" ||
                  activeRecord.execution_status === "EXECUTED_BY_OPERATOR" ? (
                    <div className="w-full text-center py-1.5 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-medium border border-emerald-200 flex items-center justify-center gap-1.5">
                      <Check className="h-3.5 w-3.5" />
                      <span>Mitigation Executed</span>
                    </div>
                  ) : activeRecord.can_act || activeRecord.authorized_persona_id === currentPersona.id ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleApprove(activeRecord.id)}
                      className="w-full h-8 text-xs font-semibold bg-zinc-100 hover:bg-zinc-200 text-zinc-900 border-zinc-300 shadow-2xs transition-all active:scale-[0.98]"
                    >
                      Authorize Mitigation
                    </Button>
                  ) : (
                    <div className="w-full text-center py-1.5 rounded-lg bg-zinc-50 text-zinc-500 text-xs border border-zinc-200 flex items-center justify-center gap-1.5">
                      <Lock className="h-3 w-3 text-zinc-400" />
                      <span>Requires {allPersonas.find((p) => p.id === activeRecord.authorized_persona_id)?.name || "Executive"} Authorization</span>
                    </div>
                  )}
                </div>
              )}

              {/* Tier 3 Technical Playbook */}
              {activeRecord.selected_tier === "TIER_3_PLAYBOOK" && (
                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400 font-mono">
                    Procedures
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
        ) : (
          <div className="rounded-xl border border-zinc-200/90 bg-white p-6 text-center text-xs text-zinc-400">
            Select an incident to inspect.
          </div>
        )}
      </div>
    </div>
  );
}
