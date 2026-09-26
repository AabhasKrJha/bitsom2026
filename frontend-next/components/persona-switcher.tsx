"use client";

import React from "react";
import { UserPersona } from "@/lib/types";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, UserCheck, Key, Eye } from "lucide-react";

interface PersonaSwitcherProps {
  personas: UserPersona[];
  currentPersonaId: string;
  onSelectPersona: (personaId: string) => void;
  pendingApprovalsForMeCount: number;
}

export function PersonaSwitcher({
  personas,
  currentPersonaId,
  onSelectPersona,
  pendingApprovalsForMeCount,
}: PersonaSwitcherProps) {
  const currentPersona = personas.find((p) => p.id === currentPersonaId) || personas[0];

  return (
    <div className="w-full rounded-2xl border border-border bg-card/60 p-4 shadow-xs backdrop-blur-xs">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-border/60">
        <div className="flex items-center gap-2">
          <UserCheck className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Active Governance Perspective (RBAC Lens)
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Eye className="h-3.5 w-3.5 text-emerald-500" />
          <span>Universal Visibility: All telemetry and audit records are shared across all roles</span>
        </div>
      </div>

      {/* Persona Pill Grid */}
      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
        {personas.map((persona) => {
          const isSelected = persona.id === currentPersonaId;
          const roleColorMap: Record<string, string> = {
            EXECUTIVE: "border-purple-500/30 bg-purple-500/10 text-purple-600 dark:text-purple-400",
            INFRASTRUCTURE: "border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400",
            OPERATIONS: "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400",
            ENGINEERING: "border-teal-500/30 bg-teal-500/10 text-teal-600 dark:text-teal-400",
          };

          return (
            <button
              key={persona.id}
              onClick={() => onSelectPersona(persona.id)}
              className={`group relative flex flex-col items-start gap-2 rounded-xl border p-3 text-left transition-all outline-none ${
                isSelected
                  ? "border-primary bg-primary/[0.04] shadow-xs ring-1 ring-primary/20"
                  : "border-border/80 bg-background/50 hover:border-border hover:bg-muted/40"
              }`}
            >
              <div className="flex w-full items-center justify-between">
                <div className="flex items-center gap-2">
                  <Avatar className="h-7 w-7 text-xs font-mono font-medium">
                    <AvatarFallback
                      className={
                        isSelected
                          ? "bg-primary text-primary-foreground font-bold"
                          : "bg-muted text-muted-foreground group-hover:bg-muted/80"
                      }
                    >
                      {persona.avatar_initials}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="text-xs font-semibold leading-tight text-foreground">
                      {persona.name}
                    </div>
                    <div className="text-[11px] text-muted-foreground leading-tight">
                      {persona.title}
                    </div>
                  </div>
                </div>

                {isSelected && (
                  <ShieldCheck className="h-4 w-4 text-primary shrink-0" />
                )}
              </div>

              <div className="flex flex-wrap items-center gap-1.5 mt-1">
                <Badge
                  variant="outline"
                  className={`text-[9px] px-1.5 py-0 font-medium ${
                    roleColorMap[persona.role_category] || "border-border text-foreground"
                  }`}
                >
                  {persona.role_category}
                </Badge>
                <span className="text-[10px] text-muted-foreground truncate max-w-[130px]" title={persona.asset_scope}>
                  {persona.asset_scope}
                </span>
              </div>

              {isSelected && pendingApprovalsForMeCount > 0 && (
                <div className="mt-1 flex items-center gap-1 text-[10px] font-medium text-amber-600 dark:text-amber-400">
                  <Key className="h-3 w-3" />
                  <span>{pendingApprovalsForMeCount} pending 1-click action{pendingApprovalsForMeCount > 1 ? "s" : ""}</span>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Selected Persona Governance Scope Banner */}
      {currentPersona && (
        <div className="mt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg bg-muted/40 px-3 py-2 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-foreground font-mono">
              {currentPersona.name} ({currentPersona.title})
            </span>
            <span className="text-muted-foreground">•</span>
            <span className="text-muted-foreground">{currentPersona.department}</span>
          </div>
          <div className="flex items-center gap-1.5 font-mono text-[11px] text-muted-foreground">
            <span className="font-semibold text-foreground">Authority Scope:</span>
            <span>{currentPersona.asset_scope}</span>
          </div>
        </div>
      )}
    </div>
  );
}
