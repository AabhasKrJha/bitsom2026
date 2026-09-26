"use client";

import React, { useState } from "react";
import { TopologyData } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Users, Server, Laptop, Network } from "lucide-react";

interface TopologyViewProps {
  topology: TopologyData | null;
}

export function TopologyView({ topology }: TopologyViewProps) {
  const [subTab, setSubTab] = useState<"users" | "nodes" | "subnets" | "devices">("users");

  if (!topology) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-12 text-center text-xs text-zinc-400">
        Loading topology...
      </div>
    );
  }

  return (
    <div className="space-y-3.5">
      {/* Tabs for Topology Navigation */}
      <Tabs
        value={subTab}
        onValueChange={(val) => setSubTab(val as "users" | "nodes" | "subnets" | "devices")}
        className="w-full"
      >
        <TabsList className="bg-zinc-100/90 border border-zinc-200/70 p-0.5 h-8">
          <TabsTrigger value="users" className="text-xs px-2.5 py-1 gap-1.5">
            <Users className="h-3.5 w-3.5" />
            <span>Personas ({topology.users.length})</span>
          </TabsTrigger>
          <TabsTrigger value="nodes" className="text-xs px-2.5 py-1 gap-1.5">
            <Server className="h-3.5 w-3.5" />
            <span>Infrastructure ({topology.infrastructure_nodes.length})</span>
          </TabsTrigger>
          <TabsTrigger value="subnets" className="text-xs px-2.5 py-1 gap-1.5">
            <Network className="h-3.5 w-3.5" />
            <span>Subnets ({topology.network_subnets.length})</span>
          </TabsTrigger>
          <TabsTrigger value="devices" className="text-xs px-2.5 py-1 gap-1.5">
            <Laptop className="h-3.5 w-3.5" />
            <span>Devices ({topology.client_devices.length})</span>
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Table Container - table-fixed with zero text wrapping */}
      <div className="rounded-xl border border-zinc-200/90 bg-white overflow-hidden shadow-2xs">
        {subTab === "users" && (
          <Table className="w-full table-fixed">
            <TableHeader className="bg-zinc-50/80 border-b border-zinc-100">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[10%] text-[11px] font-medium text-zinc-500 font-mono">ID</TableHead>
                <TableHead className="w-[18%] text-[11px] font-medium text-zinc-500">Name</TableHead>
                <TableHead className="w-[22%] text-[11px] font-medium text-zinc-500">Title</TableHead>
                <TableHead className="w-[14%] text-[11px] font-medium text-zinc-500">Role</TableHead>
                <TableHead className="w-[16%] text-[11px] font-medium text-zinc-500">Department</TableHead>
                <TableHead className="w-[20%] text-[11px] font-medium text-zinc-500">Asset Scope</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {topology.users.map((u) => (
                <TableRow key={u.id} className="text-xs hover:bg-zinc-50/70 border-b border-zinc-100/70">
                  <TableCell className="font-mono font-medium text-zinc-500 text-[11px] overflow-hidden truncate whitespace-nowrap">{u.id}</TableCell>
                  <TableCell className="font-medium text-zinc-900 overflow-hidden truncate whitespace-nowrap">{u.name}</TableCell>
                  <TableCell className="text-zinc-600 overflow-hidden truncate whitespace-nowrap">{u.title}</TableCell>
                  <TableCell className="overflow-hidden whitespace-nowrap">
                    <Badge variant="outline" className="text-[10px] font-mono bg-zinc-100 text-zinc-700 font-medium">
                      {u.role_category}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-zinc-500 overflow-hidden truncate whitespace-nowrap">{u.department}</TableCell>
                  <TableCell className="font-mono text-zinc-600 text-[11px] overflow-hidden truncate whitespace-nowrap">{u.asset_scope}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {subTab === "nodes" && (
          <Table className="w-full table-fixed">
            <TableHeader className="bg-zinc-50/80 border-b border-zinc-100">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[14%] text-[11px] font-medium text-zinc-500 font-mono">ID</TableHead>
                <TableHead className="w-[24%] text-[11px] font-medium text-zinc-500">Hostname</TableHead>
                <TableHead className="w-[16%] text-[11px] font-medium text-zinc-500 font-mono">IP Address</TableHead>
                <TableHead className="w-[20%] text-[11px] font-medium text-zinc-500">Service</TableHead>
                <TableHead className="w-[13%] text-[11px] font-medium text-zinc-500">Env</TableHead>
                <TableHead className="w-[13%] text-[11px] font-medium text-zinc-500">Tier</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {topology.infrastructure_nodes.map((n) => (
                <TableRow key={n.id} className="text-xs hover:bg-zinc-50/70 border-b border-zinc-100/70 font-mono">
                  <TableCell className="font-medium text-zinc-500 text-[11px] overflow-hidden truncate whitespace-nowrap">{n.id}</TableCell>
                  <TableCell className="font-sans font-medium text-zinc-900 overflow-hidden truncate whitespace-nowrap">{n.hostname}</TableCell>
                  <TableCell className="text-zinc-600 overflow-hidden truncate whitespace-nowrap">{n.ip_address}</TableCell>
                  <TableCell className="font-sans text-zinc-700 overflow-hidden truncate whitespace-nowrap">{n.service_name}</TableCell>
                  <TableCell className="overflow-hidden whitespace-nowrap">
                    <Badge variant="outline" className="text-[10px] font-mono bg-zinc-100 text-zinc-700">
                      {n.environment}
                    </Badge>
                  </TableCell>
                  <TableCell className="overflow-hidden whitespace-nowrap">
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-mono ${
                        n.criticality.includes("TIER_0")
                          ? "bg-red-50 text-red-700 border-red-200"
                          : n.criticality.includes("TIER_1")
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : "bg-zinc-100 text-zinc-700"
                      }`}
                    >
                      {n.criticality.replace("TIER_", "T")}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {subTab === "subnets" && (
          <Table className="w-full table-fixed">
            <TableHeader className="bg-zinc-50/80 border-b border-zinc-100">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[18%] text-[11px] font-medium text-zinc-500 font-mono">CIDR</TableHead>
                <TableHead className="w-[24%] text-[11px] font-medium text-zinc-500">Subnet</TableHead>
                <TableHead className="w-[16%] text-[11px] font-medium text-zinc-500">Type</TableHead>
                <TableHead className="w-[12%] text-[11px] font-medium text-zinc-500">Scope</TableHead>
                <TableHead className="w-[30%] text-[11px] font-medium text-zinc-500">Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {topology.network_subnets.map((s) => (
                <TableRow key={s.cidr} className="text-xs hover:bg-zinc-50/70 border-b border-zinc-100/70">
                  <TableCell className="font-mono font-medium text-zinc-900 text-[11px] overflow-hidden truncate whitespace-nowrap">{s.cidr}</TableCell>
                  <TableCell className="font-medium text-zinc-800 overflow-hidden truncate whitespace-nowrap">{s.subnet_name}</TableCell>
                  <TableCell className="overflow-hidden whitespace-nowrap">
                    <Badge variant="outline" className="text-[10px] font-mono bg-zinc-100 text-zinc-700">
                      {s.subnet_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="overflow-hidden whitespace-nowrap">
                    {s.is_shared ? (
                      <Badge variant="outline" className="text-[10px] font-mono bg-red-50 text-red-700 border-red-200">
                        SHARED
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] font-mono bg-zinc-100 text-zinc-600">
                        ISOLATED
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-zinc-500 text-[11px] overflow-hidden truncate whitespace-nowrap">{s.description}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {subTab === "devices" && (
          <Table className="w-full table-fixed">
            <TableHeader className="bg-zinc-50/80 border-b border-zinc-100">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[14%] text-[11px] font-medium text-zinc-500 font-mono">ID</TableHead>
                <TableHead className="w-[16%] text-[11px] font-medium text-zinc-500">User</TableHead>
                <TableHead className="w-[26%] text-[11px] font-medium text-zinc-500">Device</TableHead>
                <TableHead className="w-[14%] text-[11px] font-medium text-zinc-500">OS</TableHead>
                <TableHead className="w-[12%] text-[11px] font-medium text-zinc-500">Trust</TableHead>
                <TableHead className="w-[18%] text-[11px] font-medium text-zinc-500 font-mono">Fingerprint</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {topology.client_devices.map((d) => (
                <TableRow key={d.id} className="text-xs hover:bg-zinc-50/70 border-b border-zinc-100/70 font-mono">
                  <TableCell className="font-medium text-zinc-500 text-[11px] overflow-hidden truncate whitespace-nowrap">{d.id}</TableCell>
                  <TableCell className="font-sans font-medium text-zinc-900 overflow-hidden truncate whitespace-nowrap">{d.user_id}</TableCell>
                  <TableCell className="font-sans text-zinc-700 overflow-hidden truncate whitespace-nowrap">{d.device_name}</TableCell>
                  <TableCell className="text-zinc-600 overflow-hidden truncate whitespace-nowrap">{d.os_type}</TableCell>
                  <TableCell className="overflow-hidden whitespace-nowrap">
                    {d.is_trusted ? (
                      <Badge variant="outline" className="text-[10px] font-mono bg-emerald-50 text-emerald-700 border-emerald-200">
                        TRUSTED
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] font-mono bg-red-50 text-red-700 border-red-200">
                        UNVERIFIED
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-zinc-400 text-[11px] overflow-hidden truncate whitespace-nowrap">{d.hardware_fingerprint}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
