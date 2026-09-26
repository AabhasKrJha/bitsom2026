"use client";

import React, { useState } from "react";
import { LogEvent } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search } from "lucide-react";

interface LiveTelemetryFeedProps {
  logs: LogEvent[];
  totalLogsStored: number;
}

export function LiveTelemetryFeed({ logs, totalLogsStored }: LiveTelemetryFeedProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      searchTerm === "" ||
      log.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source_system.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.client_ip.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user_id.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" || log.status.toUpperCase() === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-4">
      {/* Table Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-zinc-400" />
            <input
              type="text"
              placeholder="Search logs, IPs, users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-8.5 rounded-lg border border-zinc-200 bg-white pl-8.5 pr-3 text-xs text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400 focus:outline-none w-60 sm:w-72 shadow-2xs"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="h-8.5 rounded-lg border border-zinc-200 bg-white px-2.5 text-xs text-zinc-700 focus:border-zinc-400 focus:outline-none shadow-2xs"
          >
            <option value="ALL">All Statuses</option>
            <option value="FAILURE">Failures Only</option>
            <option value="SUCCESS">Successes Only</option>
            <option value="WARN">Warnings Only</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-xs text-zinc-400 font-mono">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500" />
          <span>Live feed • {filteredLogs.length} of {totalLogsStored.toLocaleString()} events</span>
        </div>
      </div>

      {/* Table Container - table-fixed with proportional widths for ZERO SCROLL */}
      <div className="rounded-xl border border-zinc-200/90 bg-white overflow-hidden shadow-2xs">
        <Table className="w-full table-fixed">
          <TableHeader className="bg-zinc-50/80 border-b border-zinc-100">
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-[10%] text-[11px] font-medium text-zinc-500 font-mono">Time</TableHead>
              <TableHead className="w-[15%] text-[11px] font-medium text-zinc-500">Source</TableHead>
              <TableHead className="w-[18%] text-[11px] font-medium text-zinc-500">Event</TableHead>
              <TableHead className="w-[10%] text-[11px] font-medium text-zinc-500">Status</TableHead>
              <TableHead className="w-[13%] text-[11px] font-medium text-zinc-500 font-mono">Client IP</TableHead>
              <TableHead className="w-[14%] text-[11px] font-medium text-zinc-500">Target</TableHead>
              <TableHead className="w-[20%] text-[11px] font-medium text-zinc-500">Detail</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-xs text-zinc-400">
                  No telemetry records match this view.
                </TableCell>
              </TableRow>
            ) : (
              filteredLogs.slice(0, 30).map((log) => {
                const isFail = log.status === "FAILURE";
                const isSuccess = log.status === "SUCCESS";
                const isWarn = log.status === "WARN";

                return (
                  <TableRow key={log.id} className="text-xs hover:bg-zinc-50/70 border-b border-zinc-100/70 transition-colors">
                    <TableCell className="font-mono text-[11px] text-zinc-400 overflow-hidden truncate whitespace-nowrap">
                      {log.timestamp.includes("T") ? log.timestamp.split("T")[1].slice(0, 8) : log.timestamp}
                    </TableCell>
                    <TableCell className="font-medium text-zinc-800 overflow-hidden truncate whitespace-nowrap">
                      {log.source_system}
                    </TableCell>
                    <TableCell className="text-zinc-600 font-mono text-[11px] overflow-hidden truncate whitespace-nowrap">
                      <span className="px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-700">
                        {log.event_type}
                      </span>
                    </TableCell>
                    <TableCell className="overflow-hidden whitespace-nowrap">
                      {isSuccess && (
                        <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 font-mono text-[10px] px-1.5 py-0">
                          Success
                        </Badge>
                      )}
                      {isFail && (
                        <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 font-mono text-[10px] px-1.5 py-0">
                          Failure
                        </Badge>
                      )}
                      {isWarn && (
                        <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 font-mono text-[10px] px-1.5 py-0">
                          Warn
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-zinc-500 text-[11px] overflow-hidden truncate whitespace-nowrap">
                      {log.client_ip}
                    </TableCell>
                    <TableCell className="font-medium text-zinc-700 overflow-hidden truncate whitespace-nowrap">
                      {log.user_id}
                    </TableCell>
                    <TableCell className="text-zinc-500 text-[11px] overflow-hidden truncate whitespace-nowrap">
                      {log.failure_reason || "Normal baseline"}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
