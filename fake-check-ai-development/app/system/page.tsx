"use client"

import { useEffect, useState } from "react"
import { CheckCircle2, Activity, Gauge, Clock3, CircleCheck, Radio } from "lucide-react"
import { SiteHeader } from "@/components/site-header"
import { getHealth, fetchLiveHealth } from "@/lib/health"
import type { HealthStatus } from "@/lib/types"
import { formatTime, timeAgo } from "@/lib/verdict-meta"
import { cn } from "@/lib/utils"

const EVENT_TONE: Record<string, string> = {
  ok: "text-safe",
  recovered: "text-trusted",
  degraded: "text-caution",
  error: "text-risk",
}

export default function SystemPage() {
  const [health, setHealth] = useState<HealthStatus>(getHealth())
  const [isLiveTelemetry, setIsLiveTelemetry] = useState(false)

  useEffect(() => {
    let mounted = true
    async function load() {
      const data = await fetchLiveHealth()
      if (mounted) {
        setHealth(data)
        setIsLiveTelemetry(true)
      }
    }
    load()
    const timer = setInterval(load, 20000)
    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  const stats = [
    {
      label: "Search provider",
      value: health.serpapiOk ? "Operational" : "Degraded",
      icon: Activity,
      tone: health.serpapiOk ? "text-safe" : "text-risk",
    },
    { label: "Median latency", value: `${health.latencyMs} ms`, icon: Gauge, tone: "text-foreground" },
    { label: "Checks today", value: String(health.checksToday), icon: CircleCheck, tone: "text-foreground" },
    { label: "Success rate", value: `${health.successRatePct}%`, icon: Clock3, tone: "text-foreground" },
  ]

  return (
    <div className="min-h-svh bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl px-4 py-8 sm:py-12">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold tracking-tight">System status</h1>
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              <span className={cn("size-2 rounded-full", isLiveTelemetry ? "bg-emerald-500 animate-pulse" : "bg-amber-500")} />
              {isLiveTelemetry
                ? "Live FastAPI telemetry connected; 20s heartbeat active."
                : "Simulated system metrics for the demo; not live service health."}
            </p>
          </div>
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium",
              health.mode === "live"
                ? "border-safe/25 bg-safe/10 text-safe"
                : "border-caution/30 bg-caution/10 text-caution",
            )}
          >
            <CheckCircle2 className="size-4" />
            {health.mode === "live" ? "Live mode" : "Cached mode"}
          </span>
        </div>

        <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {stats.map((s) => {
            const Icon = s.icon
            return (
              <div key={s.label} className="rounded-2xl border border-border bg-card p-4">
                <Icon className={cn("size-4", s.tone)} />
                <p className="mt-3 text-xl font-semibold tabular-nums">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
            )
          })}
        </section>

        <section className="mt-6 rounded-2xl border border-border bg-card p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Fail-safe behavior</h2>
            <span className="text-xs text-muted-foreground">Last check {timeAgo(health.lastCheckAt)}</span>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            When live search slows down or errors, checks fall back to the most recent verified result instead of
            failing. Results served this way are clearly labeled with the time they were last confirmed.
          </p>
        </section>

        <section className="mt-6">
          <h2 className="mb-3 text-sm font-semibold">Recent events</h2>
          <ul className="divide-y divide-border rounded-2xl border border-border bg-card">
            {health.recentEvents.map((e, i) => (
              <li key={i} className="flex items-center gap-3 p-3.5">
                <span className={cn("size-2 shrink-0 rounded-full bg-current", EVENT_TONE[e.kind])} aria-hidden />
                <span className="min-w-0 flex-1 text-sm">{e.message}</span>
                <span className="shrink-0 text-xs text-muted-foreground">{formatTime(e.at)}</span>
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  )
}
