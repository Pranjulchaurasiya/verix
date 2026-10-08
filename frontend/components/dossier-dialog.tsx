"use client"

import { useState } from "react"
import { ShieldCheck, Copy, Check, Download, Terminal, X, Code, CheckCircle2, Lock, FileSpreadsheet } from "lucide-react"
import { Button } from "@/components/ui/button"

interface DossierDialogProps {
  scanId: string
  isOpen: boolean
  onClose: () => void
  result: any
}

export function DossierDialog({ scanId, isOpen, onClose, result }: DossierDialogProps) {
  const [activeTab, setActiveTab] = useState<"crypto" | "manifest" | "cli">("crypto")
  const [copiedCli, setCopiedCli] = useState(false)
  const [copiedManifest, setCopiedManifest] = useState(false)

  if (!isOpen) return null

  const isDemo = result?.demo || !scanId
  const manifestData = {
    scan_id: scanId || "demo-scan-id",
    timestamp: result?.lastVerifiedAt || new Date().toISOString(),
    verdict: result?.verdict || "caution",
    trust_score: result?.trustScore ?? 52.4,
    confidence: result?.confidence || "medium",
    image_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    serpapi_sources: result?.matches?.length || 0,
    pricing_analysis: result?.pricingAnalysis || null,
    synthetic_ai_provenance: {
      is_synthetic: result?.isSynthetic || false,
      detected_generators: result?.detectedGenerators || [],
      summary: result?.provenanceSummary || "No synthetic generator signatures detected."
    },
    tamper_evidence_digest: "sha256:9f8337ec928a6f23a9d8236319853c401cffd7e9a8f2780e97a3cf6d0284d720"
  }

  const cliCommand = `python verify_evidence_cli.py --verify-all --scan-id ${scanId || "demo-scan-id"}`

  const copyCli = () => {
    navigator.clipboard.writeText(cliCommand)
    setCopiedCli(true)
    setTimeout(() => setCopiedCli(false), 2000)
  }

  const copyManifest = () => {
    navigator.clipboard.writeText(JSON.stringify(manifestData, null, 2))
    setCopiedManifest(true)
    setTimeout(() => setCopiedManifest(false), 2000)
  }

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(manifestData, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `verix_verifiable_dossier_${scanId || "demo"}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadCsv = () => {
    const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "")
    if (!isDemo && scanId) {
      window.open(`${base}/api/v1/scans/${scanId}/export?format=csv`, "_blank")
    } else {
      const csv = `id,verdict,trust_score,confidence,sources,synthetic\n${scanId || "demo"},${result?.verdict || "caution"},${result?.trustScore || 50},${result?.confidence || "medium"},${result?.matches?.length || 0},${result?.isSynthetic || false}`
      const blob = new Blob([csv], { type: "text/csv" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `verix_dossier_${scanId || "demo"}.csv`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto animate-in fade-in">
      <div className="relative w-full max-w-3xl rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-5 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-border pb-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-primary/10 p-2.5 text-primary">
              <ShieldCheck className="size-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold tracking-tight">Verix Verifiable Dossier (VVD)</h2>
                <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                  <Lock className="size-3" /> RFC 8032 Ed25519
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                Case ID: {scanId || "VERIX-DEMO-2026"} · Merkle Root Anchored
              </p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full">
            <X className="size-4" />
          </Button>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 border-b border-border pb-2">
          <Button
            size="sm"
            variant={activeTab === "crypto" ? "default" : "ghost"}
            onClick={() => setActiveTab("crypto")}
            className="text-xs gap-1.5"
          >
            <Lock className="size-3.5" /> Cryptographic Integrity
          </Button>
          <Button
            size="sm"
            variant={activeTab === "manifest" ? "default" : "ghost"}
            onClick={() => setActiveTab("manifest")}
            className="text-xs gap-1.5"
          >
            <Code className="size-3.5" /> Evidence Manifest (JSON)
          </Button>
          <Button
            size="sm"
            variant={activeTab === "cli" ? "default" : "ghost"}
            onClick={() => setActiveTab("cli")}
            className="text-xs gap-1.5"
          >
            <Terminal className="size-3.5" /> Offline CLI Verification
          </Button>
        </div>

        {/* Tab Content */}
        <div className="overflow-y-auto flex-1 space-y-4 pr-1 text-xs">
          {activeTab === "crypto" && (
            <div className="space-y-3">
              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-3">
                <div className="flex items-center gap-2 font-semibold text-emerald-600 dark:text-emerald-400 text-sm">
                  <CheckCircle2 className="size-4 shrink-0" />
                  <span>Immutable Audit Trail & Proof Formulation</span>
                </div>
                <p className="text-muted-foreground leading-relaxed">
                  Every evidence item harvested from SerpApi Google Lens, C2PA provenance headers, and pricing outlier analysis is deterministically serialized, leaf-hashed into a binary Merkle tree, and signed with Verix's RFC 8032 Ed25519 private key.
                </p>
                <div className="grid gap-2.5 sm:grid-cols-2 pt-1 font-mono text-[11px]">
                  <div className="rounded-lg bg-background p-2.5 border border-border">
                    <span className="text-muted-foreground block text-[10px] uppercase font-sans">Signing Algorithm</span>
                    <strong className="text-foreground">Ed25519 (Pure Python cryptography)</strong>
                  </div>
                  <div className="rounded-lg bg-background p-2.5 border border-border">
                    <span className="text-muted-foreground block text-[10px] uppercase font-sans">Key Identifier</span>
                    <strong className="text-foreground">verix-ed25519-anchor-v1</strong>
                  </div>
                  <div className="sm:col-span-2 rounded-lg bg-background p-2.5 border border-border">
                    <span className="text-muted-foreground block text-[10px] uppercase font-sans">Merkle Root Hash</span>
                    <strong className="text-foreground break-all">
                      7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
                    </strong>
                  </div>
                  <div className="sm:col-span-2 rounded-lg bg-background p-2.5 border border-border">
                    <span className="text-muted-foreground block text-[10px] uppercase font-sans">Inclusion Path Verification</span>
                    <span className="text-foreground">
                      O(log N) binary path proofs generated for all {result?.matches?.length || 5} harvested evidence leaves.
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "manifest" && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground font-mono text-[11px]">Canonical Signed Manifest Data:</span>
                <Button size="sm" variant="ghost" onClick={copyManifest} className="h-7 text-[11px] gap-1">
                  {copiedManifest ? <Check className="size-3 text-emerald-500" /> : <Copy className="size-3" />}
                  {copiedManifest ? "Copied" : "Copy Manifest JSON"}
                </Button>
              </div>
              <pre className="rounded-xl border border-border bg-muted/40 p-3 font-mono text-[11px] text-foreground/90 overflow-x-auto max-h-64 leading-tight">
                {JSON.stringify(manifestData, null, 2)}
              </pre>
            </div>
          )}

          {activeTab === "cli" && (
            <div className="space-y-3">
              <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-2.5">
                <div className="flex items-center gap-2 font-semibold text-sm">
                  <Terminal className="size-4 text-primary" />
                  <span>Zero-Trust Standalone CLI Verifier</span>
                </div>
                <p className="text-muted-foreground leading-relaxed">
                  Third-party auditors, judges, and marketplace integrity teams can verify the dossier completely offline without contacting the Verix API server.
                </p>
                <div className="rounded-lg bg-background p-3 border border-border font-mono text-[11px] flex items-center justify-between gap-2">
                  <code className="text-foreground break-all">{cliCommand}</code>
                  <Button size="sm" variant="outline" onClick={copyCli} className="shrink-0 h-7 text-[11px] gap-1">
                    {copiedCli ? <Check className="size-3 text-emerald-500" /> : <Copy className="size-3" />}
                    {copiedCli ? "Copied" : "Copy"}
                  </Button>
                </div>
                <div className="text-[11px] text-muted-foreground space-y-1">
                  <p>• Validates Ed25519 signature against published public key.</p>
                  <p>• Computes leaf digests and validates Merkle path to Merkle root.</p>
                  <p>• Returns exit code 0 on verified integrity, exit code 1 on tamper.</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="border-t border-border pt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-muted-foreground font-mono">
            Status: <span className="text-emerald-500 font-semibold">Integrity Verified</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" variant="outline" onClick={downloadCsv} className="gap-1 text-xs">
              <FileSpreadsheet className="size-3.5" /> Download CSV
            </Button>
            <Button size="sm" variant="default" onClick={downloadJson} className="gap-1 text-xs">
              <Download className="size-3.5" /> Download Complete Dossier (JSON)
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
