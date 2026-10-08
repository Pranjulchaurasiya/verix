"use client"

import { useEffect, useRef, useState } from "react"
import { ArrowUpRight } from "lucide-react"
import { toast } from "sonner"
import type { CheckResult, Persona, BatchScanResponse } from "@/lib/types"
import { scanProduct, scanBatch } from "@/lib/scan-service"
import { addCheck } from "@/lib/history-store"
import { PersonaToggle } from "@/components/persona-toggle"
import { CheckForm, type SubmitPayload } from "@/components/check-form"
import { ResultView } from "@/components/result-view"
import { BatchResultView } from "@/components/batch-result-view"
import { ResultSkeleton } from "@/components/result-skeleton"
import { HistoryView } from "@/components/history-view"

type Phase = "idle" | "loading" | "done"

const HEADINGS: Record<Persona, { title: string; subtitle: string }> = {
  buyer: {
    title: "Check before you buy",
    subtitle: "Compare public image matches, prices and seller signals before your next purchase.",
  },
  seller: {
    title: "Protect your product photos",
    subtitle: "Find public matches and collect evidence of potential reuse for review.",
  },
}

export function CheckExperience() {
  const [persona, setPersona] = useState<Persona>("buyer")
  const [mode, setMode] = useState<"demo" | "api">("api")
  const [error, setError] = useState("")
  const [lastPayload, setLastPayload] = useState<SubmitPayload | null>(null)
  const [phase, setPhase] = useState<Phase>("idle")
  const [step, setStep] = useState(0)
  const [result, setResult] = useState<CheckResult | null>(null)
  const [batchResult, setBatchResult] = useState<BatchScanResponse | null>(null)
  const timers = useRef<ReturnType<typeof setTimeout>[]>([])

  useEffect(() => {
    return () => timers.current.forEach(clearTimeout)
  }, [])

  const runCheck = async (payload: SubmitPayload) => {
    setError("")
    setLastPayload(payload)
    setPhase("loading")
    setStep(0)
    setResult(null)
    timers.current.forEach(clearTimeout)

    timers.current = [
      setTimeout(() => setStep(1), 550),
      setTimeout(() => setStep(2), 1150),
    ]
    try {
      const res = await scanProduct(payload, persona, mode)
      setResult(res)
      setPhase("done")
      try { addCheck(res) } catch { toast.error("Result ready, but device history could not be saved.") }
    } catch (e) { setError(e instanceof Error ? e.message : "Scan failed. Please retry."); setPhase("idle") }
    finally { timers.current.forEach(clearTimeout) }
  }

  const runBatchCheck = async (items: { url: string; label?: string }[]) => {
    setError("")
    setPhase("loading")
    setStep(1)
    setResult(null)
    setBatchResult(null)
    try {
      const bRes = await scanBatch(items, persona)
      setBatchResult(bRes)
      setPhase("done")
      toast.success(`Batch assessment completed across ${bRes.totalItems} items.`)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Batch scan failed. Please retry.")
      setPhase("idle")
    }
  }

  const reset = () => {
    setPhase("idle")
    setResult(null)
    setBatchResult(null)
  }

  const heading = HEADINGS[persona]

  return (
    <div className={phase === "idle" ? "investigation-grid" : "mx-auto max-w-4xl"}>
      <div className="scan-column space-y-6">
      {phase !== "done" && (
        <div className="space-y-4">
          <div className="workspace-eyebrow"><span>THE IMAGE INTELLIGENCE WORKSPACE</span></div>
          <h1 className="workspace-title">{persona === "buyer" ? <>Check before<br />you <span>buy.</span></> : <>Your photos.<br /><span>Your evidence.</span></>}</h1>
          <p className="max-w-xl text-pretty text-base leading-relaxed text-muted-foreground">{heading.subtitle}</p>
        </div>
      )}

      {phase === "idle" && (
        <div className="space-y-5">
          {error && <div role="alert" className="rounded-xl border border-risk/40 p-4 text-sm"><p>{error}</p>{lastPayload && <button className="mt-2 underline" onClick={() => runCheck(lastPayload)}>Retry scan</button>}</div>}
          <div className="scan-workbench">
            <div className="workbench-toolbar"><span className="section-index">01 / START A CHECK</span><label className="mode-control"><span className="sr-only">Scan mode</span><select value={mode} onChange={e => setMode(e.target.value as "demo" | "api")}><option value="demo">Demo mode</option><option value="api">Connected API</option></select></label></div>
            <PersonaToggle value={persona} onChange={setPersona} />
            <CheckForm persona={persona} onSubmit={runCheck} onBatchSubmit={runBatchCheck} />
          </div>
          <div className="scan-footnote"><p>Powered by <strong>SerpApi Google Lens</strong></p><span>{mode === "demo" ? "Sample investigations only · simulated" : "API provenance unconfirmed"}</span></div>
          <details className="privacy-disclosure"><summary>Image privacy & retention</summary><p>Demo cases stay on this device. Connected scans store images and records on the backend; image links expire, and you can delete a scan from History. Avoid sensitive images while Verix is in beta.</p></details>
        </div>
      )}

      {phase === "loading" && <ResultSkeleton step={step} demo={mode === "demo" || Boolean(lastPayload?.seed.startsWith("example-"))} imageUrl={lastPayload?.imageUrl} />}

      {phase === "done" && batchResult && (
        <BatchResultView batch={batchResult} onReset={reset} />
      )}

      {phase === "done" && result && !batchResult && (
        <ResultView
          result={result}
          onReset={() => {
            reset()
            toast.success("Ready for another check")
          }}
        />
      )}
      </div>

      {phase === "idle" && (
        <aside className="case-preview">
          <div className="workspace-eyebrow"><span>THE EVIDENCE FILE</span><span>DEMO / 001</span></div>
          <div className="case-image"><img src="/demo/sneaker.png" alt="Sneaker used in the simulated investigation" /><span className="case-caption">SUBJECT A — PRODUCT PHOTOGRAPH</span></div>
          <div className="case-body"><div className="flex items-start justify-between gap-3"><h2 className="text-2xl font-medium tracking-tight">One image.<br />Five different stories.</h2><span className="case-badge">Review suggested</span></div>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">The same product photo. A reference listing at ₹12,000. Another at ₹1,900. Follow the evidence before you decide.</p>
          <div className="case-row"><span><span className="evidence-dot" />Trusted reference median</span><strong>₹11,750</strong></div>
          <div className="case-row"><span><span className="evidence-dot caution" />Lowest flagged listing</span><strong>₹1,900</strong></div>
          <div className="case-comparison"><span className="text-4xl font-medium tracking-tight">84<span className="text-xl">%</span></span><span className="text-sm text-muted-foreground">below reference price<br /><span className="text-xs">Illustrative data · not a live finding</span></span></div>
          <button className="case-action" onClick={() => runCheck({inputType:"upload",imageUrl:"/demo/sneaker.png",seed:"example-sneaker"})}>Open this investigation <ArrowUpRight className="size-5" /></button>
          </div>
        </aside>
      )}
      {phase === "idle" && <section className="recent-section"><div className="recent-heading"><div><span className="section-index">02 / YOUR WORKSPACE</span><h2>Recent investigations</h2></div><span className="text-sm text-muted-foreground">Saved on this device</span></div><HistoryView compact /></section>}
    </div>
  )
}
