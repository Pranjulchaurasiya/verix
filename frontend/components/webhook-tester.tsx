"use client"

import { useState } from "react"
import { Webhook, Send, CheckCircle2, AlertCircle, Loader2, KeyRound, Copy, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { getApiBaseUrl } from "@/lib/client-scope"

export function WebhookTester() {
  const [url, setUrl] = useState("https://httpbin.org/post")
  const [secret, setSecret] = useState("verix_enterprise_secret_2026")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [copied, setCopied] = useState(false)

  const handleTestPing = async () => {
    setLoading(true)
    setResult(null)
    try {
      const base = getApiBaseUrl()
      const res = await fetch(`${base}/api/v1/webhooks/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, secret })
      })
      const data = await res.json()
      setResult(data)
    } catch (err: any) {
      setResult({
        success: false,
        status_code: 0,
        error: err.message || "Failed to reach Verix webhook testing API"
      })
    } finally {
      setLoading(false)
    }
  }

  const copyHeader = () => {
    if (result?.signature_header) {
      navigator.clipboard.writeText(result.signature_header)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
      <div className="flex items-center gap-2.5">
        <div className="rounded-lg bg-primary/10 p-2 text-primary">
          <Webhook className="size-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold">Live Webhook Dispatcher & Simulator</h2>
          <p className="text-xs text-muted-foreground">
            Test real-time event delivery and HMAC-SHA256 signature generation to your endpoint.
          </p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground">Target Endpoint URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://your-domain.com/webhooks"
            className="w-full rounded-lg border border-border bg-muted/40 px-3 py-2 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground">HMAC Signing Secret</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={secret}
              onChange={(e) => setSecret(e.target.value)}
              placeholder="32-byte secret"
              className="w-full rounded-lg border border-border bg-muted/40 px-3 py-2 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <Button
              size="sm"
              variant="outline"
              onClick={() => setSecret(Array.from(crypto.getRandomValues(new Uint8Array(16))).map(b => b.toString(16).padStart(2, '0')).join(''))}
              title="Generate new random secret"
            >
              <KeyRound className="size-3.5" />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="text-xs text-muted-foreground">
          Subscribed Topics: <span className="font-semibold text-foreground">high_risk, pricing_anomaly, synthetic_listing</span>
        </div>
        <Button size="sm" onClick={handleTestPing} disabled={loading || !url} className="gap-1.5">
          {loading ? (
            <>
              <Loader2 className="size-3.5 animate-spin" /> Dispatching...
            </>
          ) : (
            <>
              <Send className="size-3.5" /> Send Test Event
            </>
          )}
        </Button>
      </div>

      {result && (
        <div className={`mt-3 rounded-xl border p-4 space-y-2.5 text-xs ${
          result.success ? "border-emerald-500/30 bg-emerald-500/5" : "border-amber-500/30 bg-amber-500/5"
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-semibold">
              {result.success ? (
                <>
                  <CheckCircle2 className="size-4 text-emerald-500" />
                  <span className="text-emerald-600 dark:text-emerald-400">
                    Delivered: HTTP {result.status_code} ({result.latency_ms} ms)
                  </span>
                </>
              ) : (
                <>
                  <AlertCircle className="size-4 text-amber-500" />
                  <span className="text-amber-600 dark:text-amber-400">
                    Delivery Dispatched (HTTP {result.status_code || "0 / Network Response"}) · {result.latency_ms} ms
                  </span>
                </>
              )}
            </div>
            {result.signature_header && (
              <Button size="sm" variant="ghost" onClick={copyHeader} className="h-7 text-[11px] gap-1">
                {copied ? <Check className="size-3 text-emerald-500" /> : <Copy className="size-3" />}
                {copied ? "Copied Signature" : "Copy Signature"}
              </Button>
            )}
          </div>

          {result.signature_header && (
            <div className="rounded-lg bg-background/80 p-2.5 border border-border/50">
              <span className="text-[10px] font-semibold text-muted-foreground uppercase">X-Verix-Signature Header</span>
              <p className="mt-0.5 font-mono text-[11px] text-foreground break-all">{result.signature_header}</p>
            </div>
          )}

          {result.error && (
            <p className="text-red-500 font-mono text-[11px]">{result.error}</p>
          )}
        </div>
      )}
    </div>
  )
}
