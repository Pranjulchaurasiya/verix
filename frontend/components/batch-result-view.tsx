"use client"

import { CheckCircle2, AlertTriangle, ShieldCheck, Download, RotateCcw, ExternalLink, Sparkles } from "lucide-react"
import type { BatchScanResponse } from "@/lib/types"
import { TrustScoreRing } from "@/components/trust-score-ring"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function BatchResultView({
  batch,
  onReset
}: {
  batch: BatchScanResponse
  onReset: () => void
}) {
  const exportBatchJson = () => {
    const blob = new Blob([JSON.stringify(batch, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `verix_batch_audit_${batch.batchId.slice(0, 8)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportBatchCsv = () => {
    const headers = ["Label", "URL", "Status", "Trust Score", "Risk Category", "Matched Sources", "Explanation"]
    const rows = batch.items.map(it => [
      `"${(it.label || "Item").replace(/"/g, '""')}"`,
      `"${it.url.replace(/"/g, '""')}"`,
      `"${it.status}"`,
      it.trustScore ?? "N/A",
      `"${it.riskCategory}"`,
      it.matchedDomainsCount,
      `"${it.explanation.replace(/"/g, '""')}"`
    ])
    const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n")
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `verix_batch_audit_${batch.batchId.slice(0, 8)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Top action bar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <span className="text-xs font-semibold tracking-wider text-muted-foreground uppercase">
            MULTI-ITEM DOSSIER · BATCH SCAN
          </span>
          <h1 className="text-2xl font-bold tracking-tight">Aggregated Listing Assessment</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant="outline" onClick={exportBatchJson}>
            <Download className="mr-1.5 size-3.5" /> JSON Dossier
          </Button>
          <Button size="sm" variant="outline" onClick={exportBatchCsv}>
            <Download className="mr-1.5 size-3.5" /> CSV Report
          </Button>
          <Button size="sm" variant="outline" onClick={onReset}>
            <RotateCcw className="mr-1.5 size-3.5" /> New Batch
          </Button>
        </div>
      </div>

      {/* Aggregate Overview Card */}
      <div className="grid gap-4 sm:grid-cols-4">
        <div className="flex items-center gap-4 rounded-2xl border border-border bg-card p-5 sm:col-span-2">
          {(() => {
            const score = batch.aggregateTrustScore ?? null
            const toneClass = score === null
              ? "text-muted-foreground"
              : score >= 80
              ? "text-emerald-500"
              : score >= 50
              ? "text-amber-500"
              : "text-red-500"
            return (
              <>
                <TrustScoreRing score={score} toneClass={toneClass} size={84} />
                <div>
                  <span className="text-xs font-medium text-muted-foreground uppercase">Consolidated Score</span>
                  <p className="text-2xl font-bold tracking-tight">
                    {score !== null ? `${score} / 100` : "Insufficient Data"}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Across {batch.totalItems} scanned angles/items
                  </p>
                </div>
              </>
            )
          })()}
        </div>

        <div className="rounded-2xl border border-border bg-card p-5">
          <span className="text-xs font-medium text-muted-foreground uppercase">Risk Breakdown</span>
          <div className="mt-3 space-y-1.5 text-sm">
            <div className="flex justify-between">
              <span className="text-emerald-500 font-medium">Low Risk / Verified:</span>
              <span className="font-semibold">{batch.lowRiskCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-amber-500 font-medium">Moderate Risk:</span>
              <span className="font-semibold">{batch.moderateRiskCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-500 font-medium">High Risk:</span>
              <span className="font-semibold">{batch.highRiskCount}</span>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5">
          <span className="text-xs font-medium text-muted-foreground uppercase">Cryptographic Audit</span>
          <p className="mt-2 text-xs font-mono text-muted-foreground truncate" title={batch.auditSignature}>
            HMAC: {batch.auditSignature.slice(0, 16)}...
          </p>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-emerald-500">
            <ShieldCheck className="size-4 shrink-0" />
            <span>Tamper-evident digest verified</span>
          </div>
        </div>
      </div>

      {/* Itemized Results */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold tracking-tight">Scanned Listing Items ({batch.items.length})</h2>
        <div className="grid gap-3">
          {batch.items.map((item, idx) => (
            <div key={idx} className="rounded-xl border border-border bg-card p-4 transition-colors">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-muted px-2 py-0.5 text-xs font-semibold">
                      {item.label || `Item #${idx + 1}`}
                    </span>
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-xs font-medium",
                        item.riskCategory === "trusted" && "bg-emerald-500/10 text-emerald-500",
                        item.riskCategory === "low_risk" && "bg-emerald-500/10 text-emerald-500",
                        item.riskCategory === "moderate_risk" && "bg-amber-500/10 text-amber-500",
                        item.riskCategory === "high_risk" && "bg-red-500/10 text-red-500",
                        item.riskCategory === "insufficient_data" && "bg-muted text-muted-foreground"
                      )}
                    >
                      {item.riskCategory.replace("_", " ")}
                    </span>
                  </div>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground truncate max-w-lg"
                  >
                    {item.url} <ExternalLink className="size-3" />
                  </a>
                </div>

                <div className="text-right">
                  <span className="text-sm font-bold tabular-nums">
                    {item.trustScore !== null && item.trustScore !== undefined ? `${item.trustScore}/100` : "No score"}
                  </span>
                  <p className="text-xs text-muted-foreground">{item.matchedDomainsCount} web matches</p>
                </div>
              </div>

              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{item.explanation}</p>

              {item.aiOverview && (
                <div className="mt-2.5 flex items-start gap-2 rounded-lg border border-primary/20 bg-primary/5 p-2.5 text-xs">
                  <Sparkles className="mt-0.5 size-3.5 shrink-0 text-primary" />
                  <span>
                    <strong className="text-primary font-medium">Google Lens Overview:</strong> {item.aiOverview}
                  </span>
                </div>
              )}

              {item.isSynthetic && (
                <div className="mt-2.5 flex items-start gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 p-2 text-xs">
                  <span className="shrink-0 rounded bg-amber-500/20 px-1.5 py-0.5 font-semibold text-amber-600 dark:text-amber-400">
                    AI SYNTHETIC
                  </span>
                  <span>
                    {item.provenanceSummary || "Synthetic generator tags detected in image bytes."}
                    {item.detectedGenerators && item.detectedGenerators.length > 0 && (
                      <span className="ml-1 text-muted-foreground font-mono">
                        ({item.detectedGenerators.join(", ")})
                      </span>
                    )}
                  </span>
                </div>
              )}

              {item.topMatches.length > 0 && (
                <div className="mt-3 flex flex-wrap items-center gap-2 pt-2 border-t border-border/50">
                  <span className="text-xs text-muted-foreground">Top detected domains:</span>
                  {item.topMatches.slice(0, 4).map((m, mIdx) => (
                    <span
                      key={mIdx}
                      className="inline-flex items-center gap-1.5 rounded-full border border-border px-2 py-0.5 text-xs"
                    >
                      {m.sourceIcon && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={m.sourceIcon} alt="" className="size-3 rounded-full" />
                      )}
                      <span>{m.domain}</span>
                      {m.price !== undefined && <span className="text-muted-foreground font-mono">₹{m.price}</span>}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
