"use client";

import React from "react";
import { UserPersona } from "@/lib/types";
import {
  ShieldAlert,
  Activity,
  Network,
  ChevronUp,
  Check,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

interface SidebarProps {
  currentTab: "decisions" | "telemetry" | "topology";
  onSelectTab: (tab: "decisions" | "telemetry" | "topology") => void;
  personas: UserPersona[];
  currentPersonaId: string;
  onSelectPersona: (personaId: string) => void;
  pendingApprovalsForMeCount: number;
  totalAuditsCount: number;
  totalLogsCount: number;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function Sidebar({
  currentTab,
  onSelectTab,
  personas,
  currentPersonaId,
  onSelectPersona,
  pendingApprovalsForMeCount,
  totalAuditsCount,
  totalLogsCount,
  isCollapsed,
  onToggleCollapse,
}: SidebarProps) {
  const currentPersona =
    personas.find((p) => p.id === currentPersonaId) || personas[0] || {
      id: "u_ciso",
      name: "Elena Rostova",
      title: "Chief Information Security Officer",
      role_category: "EXECUTIVE",
      department: "Security & Governance",
      asset_scope: "Enterprise Identity & Okta IAM",
      avatar_initials: "ER",
    };

  return (
    <aside
      className={`shrink-0 border-r border-zinc-200/80 bg-zinc-50/50 flex flex-col justify-between h-screen sticky top-0 select-none transition-all duration-200 ${
        isCollapsed ? "w-16" : "w-60"
      }`}
    >
      {/* Top Header - Minimalist */}
      <div>
        <div
          className={`h-12 flex items-center border-b border-zinc-200/70 px-3 ${
            isCollapsed ? "justify-center" : "justify-between"
          }`}
        >
          {!isCollapsed && (
            <span className="text-xs font-semibold tracking-tight text-zinc-900">
              Operations
            </span>
          )}

          <button
            onClick={onToggleCollapse}
            className="text-zinc-400 hover:text-zinc-700 p-1 rounded-md hover:bg-zinc-100 transition-colors"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <PanelLeftOpen className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}
          </button>
        </div>

        {/* Navigation Items (shadcn Sidebar Style) */}
        <div className="p-2 space-y-1">
          {!isCollapsed && (
            <div className="px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-400 font-mono">
              Workspace
            </div>
          )}

          <button
            onClick={() => onSelectTab("decisions")}
            className={`w-full flex items-center rounded-lg text-xs font-medium transition-all ${
              isCollapsed ? "justify-center p-2" : "justify-between px-2.5 py-1.5"
            } ${
              currentTab === "decisions"
                ? "bg-zinc-100 text-zinc-900 font-semibold border border-zinc-200/70 shadow-2xs"
                : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100/70"
            }`}
            title="Decision Governance"
          >
            <div className="flex items-center gap-2 relative">
              <ShieldAlert className="h-4 w-4 shrink-0" />
              {isCollapsed && pendingApprovalsForMeCount > 0 && (
                <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-amber-500 ring-2 ring-white" />
              )}
              {!isCollapsed && <span>Decisions</span>}
            </div>
            {!isCollapsed && (
              <div className="flex items-center gap-1.5">
                {pendingApprovalsForMeCount > 0 && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-900 font-semibold border border-amber-300">
                    {pendingApprovalsForMeCount}
                  </span>
                )}
                {totalAuditsCount > 0 && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-zinc-200 text-zinc-700">
                    {totalAuditsCount}
                  </span>
                )}
              </div>
            )}
          </button>

          <button
            onClick={() => onSelectTab("telemetry")}
            className={`w-full flex items-center rounded-lg text-xs font-medium transition-all ${
              isCollapsed ? "justify-center p-2" : "justify-between px-2.5 py-1.5"
            } ${
              currentTab === "telemetry"
                ? "bg-zinc-100 text-zinc-900 font-semibold border border-zinc-200/70 shadow-2xs"
                : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100/70"
            }`}
            title="Live Telemetry Lake"
          >
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>Telemetry</span>}
            </div>
            {!isCollapsed && totalLogsCount > 0 && (
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-zinc-200 text-zinc-700">
                {totalLogsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => onSelectTab("topology")}
            className={`w-full flex items-center rounded-lg text-xs font-medium transition-all ${
              isCollapsed ? "justify-center p-2" : "justify-between px-2.5 py-1.5"
            } ${
              currentTab === "topology"
                ? "bg-zinc-100 text-zinc-900 font-semibold border border-zinc-200/70 shadow-2xs"
                : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100/70"
            }`}
            title="Asset Scope & Topology"
          >
            <div className="flex items-center gap-2">
              <Network className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>Topology</span>}
            </div>
          </button>
        </div>
      </div>

      {/* Bottom Profile / Account Switcher (shadcn Dropdown Style) */}
      <div className="p-2 border-t border-zinc-200/80 bg-white/70">
        <DropdownMenu>
          <DropdownMenuTrigger
            className={`w-full flex items-center rounded-lg border border-zinc-200 bg-white hover:bg-zinc-50 transition-all text-left shadow-2xs outline-hidden cursor-pointer ${
              isCollapsed ? "justify-center p-1.5" : "justify-between p-2"
            }`}
          >
            <div className="flex items-center gap-2 overflow-hidden">
              <div className="h-7 w-7 rounded-full bg-zinc-100 text-zinc-800 border border-zinc-200 font-semibold text-xs flex items-center justify-center shrink-0 font-mono">
                {currentPersona.avatar_initials}
              </div>
              {!isCollapsed && (
                <div className="overflow-hidden">
                  <div className="text-xs font-semibold text-zinc-900 truncate leading-tight">
                    {currentPersona.name}
                  </div>
                  <div className="text-[10px] text-zinc-500 truncate leading-tight mt-0.5 font-mono">
                    {currentPersona.title.split("(")[0].trim()}
                  </div>
                </div>
              )}
            </div>
            {!isCollapsed && (
              <ChevronUp className="h-3.5 w-3.5 text-zinc-400 shrink-0" />
            )}
          </DropdownMenuTrigger>

          <DropdownMenuContent
            side="top"
            align="start"
            className="w-72 p-1.5 bg-white border border-zinc-200 shadow-xl rounded-xl z-50 mb-2"
          >
            <DropdownMenuGroup>
              <DropdownMenuLabel className="px-2.5 py-1 text-[11px] font-semibold text-zinc-500 uppercase tracking-wider">
                Switch Persona
              </DropdownMenuLabel>

              <DropdownMenuSeparator className="bg-zinc-100 my-1" />

              <div className="space-y-0.5">
                {personas.map((persona) => {
                  const isSelected = persona.id === currentPersonaId;
                  return (
                    <DropdownMenuItem
                      key={persona.id}
                      onClick={() => onSelectPersona(persona.id)}
                      className={`flex items-start gap-2.5 p-2 rounded-lg cursor-pointer transition-colors ${
                        isSelected
                          ? "bg-zinc-100 text-zinc-900 font-medium"
                          : "text-zinc-700 hover:bg-zinc-50"
                      }`}
                    >
                      <div
                        className={`h-6 w-6 rounded-full text-[10px] font-mono font-medium flex items-center justify-center shrink-0 mt-0.5 border ${
                          isSelected
                            ? "bg-zinc-900 text-white border-zinc-900"
                            : "bg-zinc-100 text-zinc-700 border-zinc-200"
                        }`}
                      >
                        {persona.avatar_initials}
                      </div>

                      <div className="flex-1 overflow-hidden">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-zinc-900 truncate">
                            {persona.name}
                          </span>
                          {isSelected && (
                            <Check className="h-3 w-3 text-zinc-900 shrink-0 ml-1" />
                          )}
                        </div>
                        <div className="text-[10px] text-zinc-500 truncate">
                          {persona.title}
                        </div>
                      </div>
                    </DropdownMenuItem>
                  );
                })}
              </div>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}
