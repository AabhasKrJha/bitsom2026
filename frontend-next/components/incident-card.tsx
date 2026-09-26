"use client";

import React, { useState } from "react";
import { AuditRecord, UserPersona } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import {
  Lock,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Terminal,
  Cpu,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
} from "lucide-react";

interface IncidentCardProps {
  record: AuditRecord;
  currentPersona: UserPersona;
  allPersonas: UserPersona[];
  onApprove: (auditId: string) => Promise<void>;
}

export function IncidentCard({
  record,
  currentPersona,
  allPersonas,
  onApprove,
}: IncidentCardProps) {
  const [approving, setApproving] = useState(false);
  const [showRawJev, setShowRawJev] = useState(false);
  const [copiedCmd, setCopiedCmd] = useState(false);

  const payload = record.action_payload || {};
  const authorizedPersona = allPersonas.find(
    (p) => p.id === (record.authorized_persona_id || payload.authorized_persona_id)
  );

  const isTier1 = record.selected_tier === "TIER_1_AUTOMATED";
  const isTier2 = record.selected_tier === "TIER_2_DRAFTED_HITL";
  const isTier3 = record.selected_tier === "TIER_3_PLAYBOOK";

  const isExecutedByOperator = record.execution_status === "EXECUTED_BY_OPERATOR";
  const isAwaitingApproval = record.execution_status === "AWAITING_APPROVAL";

  // Authority check
  const canAct = record.can_act ?? (record.authorized_persona_id === currentPersona.id);

  const handleApprove = async () => {
    setApproving(true);
    try {
      await onApprove(record.id);
    } finally {
      setApproving(false);
    }
  };

  const handleCopyCommand = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedCmd(true);
    setTimeout(() => setCopiedCmd(false), 2000);
  };

  return (
    <div className="rounded-xl border border-zinc-200/90 bg-white p-4.5 shadow-2xs transition-all hover:border-zinc-300 space-y-3.5">
      {/* Incident Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2.5 border-b border-zinc-100">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold text-sm font-mono text-zinc-900 tracking-tight">
              {record.attack_class}
            </span>

            {/* Tier Badge (Clean Monochrome) */}
            {isTier1 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700 font-medium border border-zinc-200">
                Tier 1 • Autonomous
              </span>
            )}
            {isTier2 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-white font-medium">
                Tier 2 • 1-Click HITL
              </span>
            )}
            {isTier3 && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-900 font-semibold border border-zinc-300">
                Tier 3 • Playbook
              </span>
            )}

            {/* Execution Status Badge */}
            {isExecutedByOperator && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-800 font-medium border border-zinc-200 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-zinc-900" />
                Executed by {authorizedPersona?.name || record.authorized_persona_id}
              </span>
            )}
            {isAwaitingApproval && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-800 font-medium border border-zinc-300">
                Awaiting Sign-Off
              </span>
            )}
            {record.execution_status === "EXECUTED" && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-600 font-medium">
                Auto-Mitigated (0ms)
              </span>
            )}
            {record.execution_status === "ADVISORY_PENDING" && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700 font-medium">
                Playbook Dispatched
              </span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500 mt-1">
            <span>Target: <strong className="text-zinc-800 font-mono">{record.target_user_id}</strong></span>
            <span>•</span>
            <span>Service: <strong className="text-zinc-800 font-mono">{record.target_service}</strong></span>
            <span>•</span>
            <span className="flex items-center gap-1 text-[11px] font-mono">
              <Clock className="h-3 w-3 text-zinc-400" />
              {record.timestamp.includes("T") ? record.timestamp.split("T")[1].slice(0, 8) : record.timestamp}
            </span>
          </div>
        </div>

        <div className="text-xs font-mono text-zinc-400 self-start sm:self-center">
          ID: <span className="text-zinc-600">{record.id.slice(0, 14)}...</span>
        </div>
      </div>

      {/* Cognitive Evaluation Proof (Clean Monochrome) */}
      <div className="rounded-lg bg-zinc-50/70 border border-zinc-200/70 p-3 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-zinc-500 font-mono">
            <Cpu className="h-3.5 w-3.5 text-zinc-700" />
            <span>TypeSafe Jev System-One Evaluation</span>
          </div>

          <button
            onClick={() => setShowRawJev(!showRawJev)}
            className="text-[11px] text-zinc-500 hover:text-zinc-900 flex items-center gap-1 font-mono"
          >
            <span>{showRawJev ? "Hide Jev JSON" : "Inspect Jev Evaluation"}</span>
            {showRawJev ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </button>
        </div>

        {/* Threat & Blast Radius as Clean Text Metrics */}
        <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-zinc-700">
          <div>
            <span className="text-zinc-400 font-sans mr-1">Threat Likelihood:</span>
            <strong className="text-zinc-900 font-bold">{(record.threat_confidence * 100).toFixed(0)}%</strong>
          </div>
          <div>
            <span className="text-zinc-400 font-sans mr-1">Blast Radius:</span>
            <strong className="text-zinc-900 font-bold">{(record.blast_radius * 100).toFixed(0)}%</strong>
          </div>
          {payload.target && (
            <div className="text-zinc-500 truncate max-w-xs">
              <span className="text-zinc-400 font-sans mr-1">Target Asset:</span>
              <span>{payload.target}</span>
            </div>
          )}
        </div>

        {/* Decision Engine Logic */}
        <div className="text-xs text-zinc-700 bg-white rounded p-2 border border-zinc-200/60 leading-relaxed font-sans">
          <span className="font-semibold text-zinc-900 mr-1.5">Decision Logic:</span>
          {record.reason}
        </div>

        {/* Expandable Raw Jev Output */}
        {showRawJev && record.jev_raw_evaluation && (
          <div className="rounded bg-zinc-900 p-2.5 font-mono text-[11px] text-emerald-400 overflow-x-auto max-h-44">
            <pre>{JSON.stringify(record.jev_raw_evaluation, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* TIER 1: Machine Autonomously Executed (Monochrome) */}
      {isTier1 && (
        <div className="rounded-lg border border-zinc-200 bg-zinc-50/40 p-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-zinc-900 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-zinc-800" />
              Machine Autonomous Execution Receipt
            </span>
            <span className="font-mono text-[10px] text-zinc-500">0ms Latency</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs font-mono">
            <div className="rounded bg-white p-2 border border-zinc-200/80">
              <div className="text-[10px] text-zinc-400 font-sans uppercase">Action</div>
              <div className="font-medium text-zinc-800 truncate">{payload.title || "Drop IP at Perimeter"}</div>
            </div>
            <div className="rounded bg-white p-2 border border-zinc-200/80">
              <div className="text-[10px] text-zinc-400 font-sans uppercase">Enforcement Point</div>
              <div className="font-medium text-zinc-800 truncate">{payload.execution_receipt?.enforcement_point || "Cloudflare Enterprise WAF"}</div>
            </div>
            <div className="rounded bg-white p-2 border border-zinc-200/80">
              <div className="text-[10px] text-zinc-400 font-sans uppercase">Receipt Rule ID</div>
              <div className="font-medium text-zinc-800 truncate">{payload.execution_receipt?.rule_id || "WAF-AUTO-9418"}</div>
            </div>
          </div>
        </div>
      )}

      {/* TIER 2: 1-Click Human-In-The-Loop Draft (Monochrome) */}
      {isTier2 && (
        <div className="rounded-lg border border-zinc-200 bg-white p-3.5 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="text-xs font-semibold text-zinc-900">
                {payload.title || "Null-Route Subnet at Core Perimeter"}
              </div>
              <div className="text-xs text-zinc-500 mt-0.5">
                Authority Required: <strong className="text-zinc-800 font-mono">{authorizedPersona?.name || record.authorized_persona_id}</strong>
              </div>
            </div>

            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-100 text-zinc-700 border border-zinc-200 self-start sm:self-center">
              1-Click Mitigation
            </span>
          </div>

          {payload.blast_radius_guardrail && (
            <div className="flex items-start gap-2 rounded bg-zinc-50 border border-zinc-200 p-2 text-xs text-zinc-700">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-zinc-800 mt-0.5" />
              <div>
                <span className="font-semibold text-zinc-900">Guardrail Note: </span>
                {payload.blast_radius_guardrail}
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-zinc-100">
            <div className="text-xs text-zinc-500">
              {isExecutedByOperator ? (
                <span className="text-zinc-900 font-medium flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-zinc-900" />
                  Mitigation authorized and executed by {authorizedPersona?.name || record.authorized_persona_id}.
                </span>
              ) : canAct ? (
                <span className="text-zinc-800 font-medium">
                  You hold governance authority to execute this mitigation.
                </span>
              ) : (
                <span className="text-zinc-400">
                  Visible in scope. 1-click execution authority is held by {authorizedPersona?.name || record.authorized_persona_id}.
                </span>
              )}
            </div>

            <div>
              {isExecutedByOperator ? (
                <Button variant="outline" size="sm" disabled className="h-8 gap-1.5 text-xs border-zinc-200 text-zinc-700 bg-zinc-50">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Action Completed</span>
                </Button>
              ) : canAct ? (
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleApprove}
                  disabled={approving}
                  className="h-8 bg-zinc-900 hover:bg-zinc-800 text-white font-medium text-xs gap-1.5 shadow-2xs"
                >
                  <span>{approving ? "Executing..." : payload.button_label || "Authorize Mitigation"}</span>
                </Button>
              ) : (
                <Tooltip>
                  <TooltipTrigger>
                    <Button variant="outline" size="sm" disabled className="h-8 gap-1.5 text-xs border-zinc-200 bg-zinc-50 text-zinc-400 cursor-not-allowed">
                      <Lock className="h-3.5 w-3.5" />
                      <span>Locked: {authorizedPersona?.title.split("(")[0].trim() || "Leadership"} Sign-Off</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs text-xs bg-zinc-900 text-white">
                    Governance Policy: Only {authorizedPersona?.name} holds cryptographic execution authority for {authorizedPersona?.asset_scope}.
                  </TooltipContent>
                </Tooltip>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TIER 3: Technical Mitigation Playbook (Monochrome) */}
      {isTier3 && (
        <div className="rounded-lg border border-zinc-200 bg-zinc-50/30 p-3.5 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="text-xs font-semibold text-zinc-900">
              Automated Action Rejected • Technical Orchestration Required
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-100 text-zinc-700 font-medium border border-zinc-200">
              Est. Recovery: {payload.estimated_recovery_time || "~15 mins"}
            </span>
          </div>

          <div className="rounded bg-white border border-zinc-200 p-2 text-xs text-zinc-700">
            <span className="font-semibold text-zinc-900">Trigger: </span>
            {payload.blast_radius_explanation ||
              "Autonomous execution rejected due to high blast radius across production services."}
          </div>

          <div className="space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 font-mono">
              Mitigation Steps:
            </div>
            <div className="grid grid-cols-1 gap-1 text-xs">
              {(payload.technical_steps || [
                "1. Isolate compromised worker nodes from internal service mesh",
                "2. Invalidate leaked AWS IAM temporary credentials & rotate KMS master keys",
                "3. Re-route live traffic through emergency backup cluster",
                "4. Conduct forensic audit on container runtime memory dumps"
              ]).map((step: string, idx: number) => (
                <div
                  key={idx}
                  className="flex items-start gap-2 rounded bg-white p-2 border border-zinc-200/80 font-mono text-[11px]"
                >
                  <span className="text-zinc-400 font-bold">{idx + 1}.</span>
                  <span className="text-zinc-800">{step.replace(/^\d+\.\s*/, "")}</span>
                </div>
              ))}
            </div>
          </div>

          {payload.verification_command && (
            <div className="rounded bg-zinc-900 p-2.5 font-mono text-xs text-zinc-200 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 overflow-x-auto">
                <Terminal className="h-3.5 w-3.5 text-zinc-400 shrink-0" />
                <span className="text-zinc-100 select-all">{payload.verification_command}</span>
              </div>
              <Button
                variant="ghost"
                size="icon-xs"
                onClick={() => handleCopyCommand(payload.verification_command || "")}
                className="text-zinc-400 hover:text-white"
                title="Copy verification command"
              >
                {copiedCmd ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
