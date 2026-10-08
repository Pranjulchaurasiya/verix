"use client"

import { useState } from "react"
import { Check, Info, Clock, ArrowLeft, Copy, RotateCcw, Download, ShieldAlert, FileText } from "lucide-react"
import type { CheckResult } from "@/lib/types"
import { VERDICT_META, toneClasses, formatTime } from "@/lib/verdict-meta"
import { TrustScoreRing } from "@/components/trust-score-ring"
import { MatchList } from "@/components/match-list"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { EvidencePanel } from "@/components/evidence-panel"
import { MerkleVerifyBadge } from "@/components/merkle-verify-badge"
import { TakedownDialog } from "@/components/takedown-dialog"
import { PricingDistributionCard } from "@/components/pricing-distribution-card"
import { DossierDialog } from "@/components/dossier-dialog"

const CONFIDENCE_LABEL: Record<CheckResult["confidence"], string> = {
  low: "Low confidence",
  medium: "Medium confidence",
  high: "High confidence",
}

export function ResultView({ result, onReset }: { result: CheckResult; onReset?: () => void }) {
  const [takedownOpen, setTakedownOpen] = useState(false)
  const [dossierOpen, setDossierOpen] = useState(false)
  const meta = VERDICT_META[result.verdict]
  const tone = toneClasses(meta.tone)

  const handleExport = (format: "json" | "csv" = "json") => {
    if (result.demo || !result.id) {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `verix_audit_${result.id || "demo"}.json`
      a.click()
      URL.revokeObjectURL(url)
      return
    }
    const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "")
    window.open(`${base}/api/v1/scans/${result.id}/export?format=${format}`, "_blank")
  }

  return (
    <div className="result-workspace min-w-0 max-w-full space-y-6 overflow-x-hidden">
      {onReset && (
        <Button variant="ghost" size="sm" onClick={onReset} className="-ml-2 gap-1.5 text-muted-foreground">
          <ArrowLeft className="size-4" /> Check another
        </Button>
      )}

      {result.degraded && (
        <div className="flex items-start gap-2 rounded-lg border border-caution/30 bg-caution/10 p-3 text-sm">
          <Clock className="mt-0.5 size-4 shrink-0 text-caution" />
          <p className="text-foreground">
            Live search was briefly unavailable, so this is the last verified result from{" "}
            <span className="font-medium">{formatTime(result.lastVerifiedAt)}</span>.
          </p>
        </div>
      )}

      <div className="result-heading"><div><span className="section-index">INVESTIGATION / EVIDENCE REPORT</span><h1>Follow the evidence.</h1></div><span className="result-state">{result.demo ? "DEMO EVIDENCE" : result.degraded ? "CACHED EVIDENCE" : "API RESPONSE"}</span></div>
      <div className="flex flex-wrap items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 p-3">
        <span className="mr-auto text-sm text-muted-foreground">Interactive report · click a source below to inspect its evidence.</span>
        <Button size="sm" variant="default" className="gap-1.5" onClick={() => setDossierOpen(true)}>
          <FileText className="size-3.5" /> Inspect Dossier
        </Button>
        {result.persona === "seller" && (
          <Button size="sm" variant="default" className="bg-amber-600 hover:bg-amber-700 text-white gap-1.5" onClick={() => setTakedownOpen(true)}>
            <ShieldAlert className="size-3.5" /> Takedown Notice
          </Button>
        )}
        <Button size="sm" variant="outline" onClick={() => handleExport("json")}><Download className="size-3.5" /> Export Dossier</Button>
        <Button size="sm" variant="outline" onClick={() => document.querySelector("[data-evidence-panel]")?.scrollIntoView({ behavior: "smooth" })}><Copy className="size-3.5" /> Evidence trail</Button>
        {onReset && <Button size="sm" variant="outline" onClick={onReset}><RotateCcw className="size-3.5" /> New check</Button>}
      </div>
      <div className={cn("result-summary flex min-w-0 flex-col gap-6 overflow-hidden rounded-xl border p-6", tone.border)}>
        <div className="flex w-full shrink-0 flex-wrap items-center justify-center gap-5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={result.imageUrl || "/placeholder.svg"}
            alt="Submitted product"
            className="size-24 shrink-0 rounded-lg border border-border object-cover"
          />
          <TrustScoreRing score={result.trustScore} toneClass={tone.ring} size={96} />
        </div>

        <div className="w-full min-w-0 break-words">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className={cn("text-2xl font-medium tracking-tight", tone.text)}>{meta.label}</h2>
            <span className="rounded-full border border-border bg-background/60 px-2 py-0.5 text-xs font-medium text-muted-foreground">
              {CONFIDENCE_LABEL[result.confidence]}
            </span>
          </div>
          <p className="mt-1 text-sm leading-relaxed text-foreground/90">{result.explanation}</p>
          {result.aiOverview && (
            <div className="mt-3 rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-foreground/90">
              <span className="font-semibold text-primary">Google Lens AI Overview:</span> {result.aiOverview}
            </div>
          )}
          {result.isSynthetic && (
            <div className="mt-3 flex items-start gap-2.5 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-foreground/90">
              <span className="shrink-0 rounded bg-amber-500/20 px-1.5 py-0.5 font-semibold text-amber-600 dark:text-amber-400">
                AI SYNTHETIC MARKER
              </span>
              <div>
                <p className="font-medium text-foreground">
                  {result.provenanceSummary || "Synthetic generator metadata detected in image bytes."}
                </p>
                {result.detectedGenerators && result.detectedGenerators.length > 0 && (
                  <p className="mt-1 text-muted-foreground">
                    Signatures: {result.detectedGenerators.join(", ")}
                  </p>
                )}
              </div>
            </div>
          )}
          {result.trustScore !== null && <p className="mt-2 text-xs text-muted-foreground">Evidence score summarizes public web signals. It does not authenticate a physical item or verify a seller.</p>}
          <p className="mt-2 text-sm text-muted-foreground">{result.demo ? "Simulated matches" : "Public matches returned"}: {result.matches.length} sources</p>
          {result.productAvailability && result.productAvailability !== "unknown" && <p className={cn("mt-2 inline-flex rounded-full px-2 py-1 text-xs font-medium", result.productAvailability === "in_stock" ? "bg-trusted/10 text-trusted" : "bg-caution/10 text-caution")}>
            {result.productAvailability === "in_stock" ? "Currently listed as available" : result.productAvailability === "discontinued" ? "Retailer marks this product as discontinued" : "Retailer marks this product as unavailable"}
          </p>}
        </div>
      </div>

      <MerkleVerifyBadge scanId={result.id} demo={result.demo} />

      <PricingDistributionCard pricingAnalysis={result.pricingAnalysis} />

      <section className="rounded-xl border border-border bg-card p-4" aria-label="Evidence coverage">
        <h3 className="text-sm font-semibold">What this check covered</h3>
        <div className="mt-2 grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
          <p>Public listing links: <strong className="text-foreground">{result.matches.length}</strong></p>
          <p>Distinct host domains: <strong className="text-foreground">{new Set(result.matches.map(match => match.domain.replace(/^www\./, ""))).size}</strong></p>
          <p>Seller identity: <strong className="text-foreground">Not verified</strong></p>
          <p>Physical item authenticity: <strong className="text-foreground">Not verified</strong></p>
        </div>
      </section>

      <div data-evidence-panel><EvidencePanel result={result} /></div>
      {/* Signals */}
      {result.signals.length > 0 && (
        <section className="rounded-2xl border border-border bg-card p-5">
          <h3 className="text-sm font-semibold">{result.verdict === "high_risk" ? "Why this was flagged" : "What the evidence shows"}</h3>
          <ul className="mt-3 space-y-2">
            {result.signals.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-foreground/90">
                <Check className={cn("mt-0.5 size-4 shrink-0", tone.text)} />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Matches */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">
            Where this photo appears{" "}
            <span className="font-normal text-muted-foreground">({result.matches.length})</span>
          </h3>
        </div>
        <MatchList matches={result.matches} currency={result.currency} />
      </section>

      <p className="flex items-start gap-2 rounded-lg bg-muted/60 p-3 text-xs leading-relaxed text-muted-foreground">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        This is a risk signal to help you decide — not a definitive verdict on any seller or product. Always confirm the
        seller, reviews and return policy before you pay.
      </p>

      <TakedownDialog
        scanId={result.id}
        isOpen={takedownOpen}
        onClose={() => setTakedownOpen(false)}
        demo={result.demo}
      />

      <DossierDialog
        scanId={result.id}
        isOpen={dossierOpen}
        onClose={() => setDossierOpen(false)}
        result={result}
      />
    </div>
  )
}

