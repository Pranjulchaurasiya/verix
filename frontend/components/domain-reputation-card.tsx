"use client"

import { Globe, ShieldAlert, ShieldCheck, AlertTriangle, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"

interface DomainReputationCardProps {
  domainReputation?: {
    domain?: string
    status?: "trusted" | "suspicious" | "caution" | "neutral" | "unknown"
    trust_score?: number | null
    verdict_label?: string
    warning_signals?: string[]
    snippet_samples?: string[]
    sources_analyzed?: number
    is_whitelisted?: boolean
  }
}

export function DomainReputationCard({ domainReputation }: DomainReputationCardProps) {
  if (!domainReputation || !domainReputation.domain) return null

  const status = domainReputation.status || "neutral"
  const isTrusted = status === "trusted"
  const isSuspicious = status === "suspicious"
  const isCaution = status === "caution"

  const statusTone = isTrusted
    ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400"
    : isSuspicious
    ? "border-red-500/30 bg-red-500/5 text-red-600 dark:text-red-400"
    : isCaution
    ? "border-amber-500/30 bg-amber-500/5 text-amber-600 dark:text-amber-400"
    : "border-border bg-card text-muted-foreground"

  return (
    <div className="rounded-xl border border-border bg-card p-4 transition-all">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/50 pb-3">
        <div className="flex items-center gap-2">
          <Globe className="size-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">
            Domain Trust & Scam Signal Analysis
          </h3>
          <span className="rounded bg-muted px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
            SerpApi Google Web
          </span>
        </div>
        {domainReputation.trust_score !== null && domainReputation.trust_score !== undefined && (
          <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold border", statusTone)}>
            {isTrusted ? <ShieldCheck className="size-3.5" /> : isSuspicious ? <ShieldAlert className="size-3.5" /> : <AlertTriangle className="size-3.5" />}
            {domainReputation.trust_score}/100 Trust Score
          </span>
        )}
      </div>

      <div className="mt-3 space-y-2.5 text-sm">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <span className="text-xs text-muted-foreground">Storefront Domain:</span>
          <span className="font-mono text-xs font-semibold text-foreground">{domainReputation.domain}</span>
        </div>

        <p className="text-xs leading-relaxed text-foreground/90">
          {domainReputation.verdict_label || "No scam signals found in public consumer forum crawls."}
        </p>

        {domainReputation.warning_signals && domainReputation.warning_signals.length > 0 && (
          <div className="rounded-lg border border-red-500/20 bg-red-500/5 p-3 text-xs text-red-600 dark:text-red-400 space-y-1">
            <span className="font-semibold block">Flagged Public Forum Signals:</span>
            <ul className="list-disc pl-4 space-y-0.5">
              {domainReputation.warning_signals.map((sig, idx) => (
                <li key={idx} className="leading-snug">{sig}</li>
              ))}
            </ul>
          </div>
        )}

        {domainReputation.snippet_samples && domainReputation.snippet_samples.length > 0 && (
          <div className="rounded-lg border border-border/50 bg-muted/40 p-2.5 text-[11px] text-muted-foreground">
            <span className="font-medium text-foreground block mb-1">Public Web Snippet:</span>
            <p className="italic leading-relaxed line-clamp-2">"{domainReputation.snippet_samples[0]}"</p>
          </div>
        )}
      </div>
    </div>
  )
}
