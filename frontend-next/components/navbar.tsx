"use client";

import React, { useState } from "react";
import { RefreshCw, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { resetDemoDatabase } from "@/lib/api";

interface NavbarProps {
  pageTitle: string;
  totalLogs: number;
  totalAudits: number;
  onRefresh: () => void;
}

export function Navbar({
  pageTitle,
  totalLogs,
  totalAudits,
  onRefresh,
}: NavbarProps) {
  const [resetting, setResetting] = useState(false);

  const handleReset = async () => {
    if (!confirm("Reset database to clean demo state? All logs and audit decisions will be cleared.")) {
      return;
    }
    setResetting(true);
    try {
      await resetDemoDatabase();
      onRefresh();
    } catch (err) {
      console.error("Failed to reset database", err);
    } finally {
      setResetting(false);
    }
  };

  return (
    <header className="h-14 border-b border-zinc-200/80 bg-white px-5 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Left: Section Header */}
      <div className="flex items-center gap-2 text-xs">
        <span className="font-semibold text-zinc-900">{pageTitle}</span>
        <span className="text-zinc-300 ml-1.5">•</span>
        <span className="text-zinc-400 font-mono text-[11px]">
          {totalAudits} incidents • {totalLogs.toLocaleString()} events
        </span>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          className="h-7.5 text-xs border-zinc-200 text-zinc-700 hover:bg-zinc-50 gap-1.5 shadow-2xs"
        >
          <RefreshCw className="h-3 w-3" />
          <span>Sync</span>
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleReset}
          disabled={resetting}
          className="h-7.5 text-xs border-zinc-200 text-zinc-600 hover:text-red-600 hover:bg-red-50 hover:border-red-200 gap-1.5 shadow-2xs"
          title="Reset database to fresh state"
        >
          <RotateCcw className="h-3 w-3" />
          <span>{resetting ? "Resetting..." : "Reset"}</span>
        </Button>
      </div>
    </header>
  );
}
