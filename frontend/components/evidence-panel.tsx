"use client"

import { useState } from "react"
import type { CheckResult } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { formatPrice } from "@/lib/verdict-meta"

export function EvidencePanel({ result }: { result: CheckResult }) {
  const [notice, setNotice] = useState("")
  const flagged = result.matches.filter(m => m.flagged)
  const recognizedCount = result.matches.filter(m => m.whitelisted).length
  const otherCount = result.matches.length - recognizedCount
  const recommendation = result.recommendation || (result.persona === "seller" ? "Review each match against your authorized sellers before contacting a site. A match does not establish ownership or permission." : "Confirm the seller, product details and return policy independently before purchasing.")
  function exportReport() {
    const report = { product: "Verix", mode: result.demo ? "Simulated demo evidence" : result.provenance === "cached" ? "Cached API evidence" : result.provenance === "development_fallback" ? "Development fallback" : "Live SerpApi evidence", ...result, recommendation, limitations: "Image similarity does not prove authenticity, original ownership, or unauthorized reuse. Prices may differ by product variant and date. Trusted platforms do not guarantee individual sellers." }
    const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }))
    const link = document.createElement("a")
    link.href = url; link.download = `verix-evidence-${result.id.replace(/[^a-z0-9_-]/gi, "")}.json`; link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    setNotice("Evidence report downloaded as JSON.")
  }
  return <section className="min-w-0 max-w-full space-y-5 overflow-hidden rounded-2xl border border-border bg-card p-5">
    <div className="flex flex-wrap items-center justify-between gap-3"><h3 className="font-semibold">{result.persona === "seller" ? "Creator protection · Photo reuse audit" : "Evidence trail"}</h3><span className="text-xs text-primary">{result.demo ? "Demo mode · simulated matches" : result.provenance === "cached" ? "Cached evidence" : result.provenance === "development_fallback" ? "Development fallback" : result.provenance === "live_serpapi" ? "Live SerpApi evidence" : "Evidence provenance unavailable"}</span></div>
    <p className="text-sm text-muted-foreground">Powered by SerpApi Google Lens{result.demo ? " · integration preview; no live search performed" : ""}</p>
    {result.persona === "seller" && <p className="text-sm"><strong className="text-primary">{flagged.length}</strong> matches on sources needing review. Authorization is not established by image matching.</p>}
    {result.matches.length > 0 && <div className="space-y-2 rounded-xl border border-border bg-background/30 p-4">
      <h4 className="font-semibold">Source-host coverage</h4>
      <div className="flex h-3 overflow-hidden rounded-full bg-secondary" role="img" aria-label={`${recognizedCount} listings on recognized platform hosts; ${otherCount} on other hosts`}>
        {recognizedCount > 0 && <div className="bg-trusted" style={{ width: `${recognizedCount / result.matches.length * 100}%` }} />}
        {otherCount > 0 && <div className="bg-caution" style={{ width: `${otherCount / result.matches.length * 100}%` }} />}
      </div>
      <p className="text-xs text-muted-foreground">{recognizedCount} recognized-host listing(s) · {otherCount} other-host listing(s). Host category does not verify a seller or item.</p>
    </div>}
    <ol className="min-w-0 space-y-3 border-l border-primary/30 pl-5">
      <li><p className="font-medium">01 · Submitted image</p><p className="text-sm text-muted-foreground">{new Date(result.createdAt).toLocaleString()}</p></li>
      <li><p className="font-medium">02 · Recognized platform hosts</p><p className="text-sm text-muted-foreground">{result.matches.filter(m => m.whitelisted).map(m => m.domain).join(" · ") || "No recognized host found"}</p><p className="text-xs text-muted-foreground">Host recognition does not verify the seller, item or original source.</p></li>
      <li className="min-w-0"><p className="font-medium">03 · Matched listings</p><div className="mt-2 grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-2">{result.matches.map((m,i) => <div key={`${m.url}-${i}`} className={`min-w-0 max-w-full overflow-hidden rounded-lg border p-3 ${m.flagged ? "border-caution/40 bg-caution/5" : "border-primary/20"}`}><p className="break-words text-sm font-medium [overflow-wrap:anywhere]">{m.domain}</p><p className="break-words text-xs text-muted-foreground [overflow-wrap:anywhere]">{m.flagged ? "Review suggested" : m.whitelisted ? "Recognized platform host" : "Unverified source"} · {typeof m.price === "number" ? formatPrice(m.price, m.currency) : "Price unavailable"}</p></div>)}</div></li>
    </ol>
    <p className="text-xs text-muted-foreground">Listing prices, when shown, are source-reported values. Verix has not confirmed an exact product match or a comparable price benchmark.</p>
    <div className="rounded-xl bg-secondary/50 p-4"><h4 className="mb-2 font-semibold">Recommended next step</h4><p className="text-sm text-muted-foreground">{recommendation}</p></div>
    <details className="rounded-lg border border-border p-3 text-sm text-muted-foreground"><summary className="cursor-pointer font-medium text-foreground">How this works and limitations</summary><p className="mt-2">Public image matches provide context, not proof of authenticity or ownership. A scored report requires at least two distinct source domains. Seller identity and physical item authenticity are not verified. Retrieved times describe when Verix searched, not when listings were published. Cached evidence can be out of date.</p>{result.persona === "seller" && <p className="mt-2">Check matches against your authorized partners, preserve dated evidence and confirm ownership before using a platform’s rights-reporting process.</p>}</details>
    <div className="flex flex-wrap gap-2"><Button onClick={exportReport}>Export evidence report</Button><Button variant="outline" onClick={async () => { try { await navigator.clipboard.writeText([`Verix · ${result.demo ? "Simulated demo" : "API evidence"}`, result.explanation, ...result.matches.map(m => m.url).filter(Boolean), recommendation].join("\n")); setNotice("Evidence copied.") } catch { setNotice("Clipboard unavailable. Export the report to save evidence links.") } }}>Copy evidence</Button></div>
    <p role="status" className="text-sm text-muted-foreground">{notice}</p>
  </section>
}
