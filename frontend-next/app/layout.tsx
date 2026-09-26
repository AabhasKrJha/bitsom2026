import type { Metadata } from "next";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";

export const metadata: Metadata = {
  title: "Sentix AutoOps • Autonomous Cognitive Cybersecurity Governance",
  description:
    "TypeSafe Jev System-One powered autonomous cybersecurity governance with strict single-tier decision enforcement and RBAC 1-click execution.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-white text-zinc-900 font-sans antialiased selection:bg-zinc-200">
        <TooltipProvider delay={100}>{children}</TooltipProvider>
      </body>
    </html>
  );
}
