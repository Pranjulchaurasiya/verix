"use client"

import { useState, useEffect } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { Loader2, Clock, Globe, Shield, Activity, Cpu } from "lucide-react"

const STAGES = [
  {
    id: 1,
    title: "Extracting product media & perceptual hashes",
    subtitle: "Analyzing image bytes, EXIF metadata, and listing DOM",
    icon: Cpu,
    thresholdSec: 0,
  },
  {
    id: 2,
    title: "Querying SerpApi Google Lens visual index",
    subtitle: "Matching global e-commerce listings, thumbnails, and availability",
    icon: Globe,
    thresholdSec: 1.8,
  },
  {
    id: 3,
    title: "Scanning C2PA credentials & AI generator signatures",
    subtitle: "Detecting Midjourney, Stable Diffusion, DALL-E, and SynthID watermarks",
    icon: Shield,
    thresholdSec: 4.5,
  },
  {
    id: 4,
    title: "Evaluating pricing distribution & platform registry",
    subtitle: "Cross-referencing median retail price fences & trusted marketplaces",
    icon: Activity,
    thresholdSec: 7.0,
  },
  {
    id: 5,
    title: "Anchoring cryptographic Merkle inclusion proofs",
    subtitle: "Signing immutable evidence package with RFC 8032 Ed25519",
    icon: Clock,
    thresholdSec: 9.5,
  },
]

export function ResultSkeleton({ step = 0, demo = true, imageUrl }: { step?: number; demo?: boolean; imageUrl?: string }) {
  const [elapsedSec, setElapsedSec] = useState(0)

  useEffect(() => {
    const start = Date.now()
    const timer = setInterval(() => {
      const diff = (Date.now() - start) / 1000
      setElapsedSec(diff)
    }, 100)
    return () => clearInterval(timer)
  }, [])

  // Calculate dynamic progress percent (0% to ~95% while waiting)
  const progressPercent = Math.min(
    95,
    demo
      ? Math.min(95, elapsedSec * 60)
      : elapsedSec < 2
      ? 15 + elapsedSec * 15
      : elapsedSec < 6
      ? 45 + (elapsedSec - 2) * 10
      : 85 + Math.min(10, (elapsedSec - 6) * 1.5)
  )

  // Current active stage
  const currentStageIndex = STAGES.findIndex((s, idx) => {
    const nextStage = STAGES[idx + 1]
    return !nextStage || elapsedSec < nextStage.thresholdSec
  })

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header with live timer and radar indicator */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-4">
        <div className="flex items-center gap-3">
          <span className="relative flex size-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
            <span className="relative inline-flex size-3 rounded-full bg-primary" />
          </span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-foreground">
                {demo ? "Simulating Investigation" : "Live Visual Intelligence Scan"}
              </span>
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-mono font-medium text-primary">
                SerpApi Google Lens
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {demo
                ? "Demonstrating pre-computed evidence pipeline..."
                : "Inspecting live marketplace matches, pricing distribution, and image provenance..."}
            </p>
          </div>
        </div>

        {/* Live Elapsed Stopwatch */}
        <div className="flex items-center gap-2 rounded-xl bg-background/80 px-3.5 py-1.5 border border-border shadow-sm">
          <Clock className="size-3.5 text-primary animate-spin" />
          <span suppressHydrationWarning className="text-xs font-mono font-bold text-foreground">
            {elapsedSec.toFixed(1)}s
          </span>
          <span className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">
            Elapsed
          </span>
        </div>
      </div>

      {/* Real-time Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground font-mono">
          <span>PIPELINE PROGRESS</span>
          <span suppressHydrationWarning className="text-primary font-bold">{Math.round(progressPercent)}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted/60 border border-border/50">
          <div
            className="h-full bg-primary transition-all duration-300 ease-out rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Main Skeleton Placeholder */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-5">
          {imageUrl && !imageUrl.includes("link-preview.png") ? (
            <div className="relative size-24 shrink-0 overflow-hidden rounded-xl border border-border bg-muted/20">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={imageUrl} alt="Analyzing product" className="size-full object-cover" />
              <div className="absolute inset-0 bg-primary/10 animate-pulse pointer-events-none" />
            </div>
          ) : (
            <Skeleton className="size-24 shrink-0 rounded-xl" />
          )}
          <Skeleton className="size-24 shrink-0 rounded-full" />
          <div className="flex-1 min-w-[200px] space-y-3">
            <Skeleton className="h-6 w-48 rounded-lg" />
            <Skeleton className="h-4 w-full max-w-md rounded" />
            <Skeleton className="h-4 w-3/4 max-w-sm rounded" />
          </div>
        </div>
      </div>

      {/* Multi-Stage Step Tracker */}
      <div className="rounded-2xl border border-border bg-card p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-border/60 pb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Execution Stages
          </span>
          <span className="text-xs text-muted-foreground">
            Stage {Math.max(1, currentStageIndex + 1)} of {STAGES.length}
          </span>
        </div>

        <ul className="space-y-3">
          {STAGES.map((stage, idx) => {
            const isCompleted = idx < currentStageIndex
            const isCurrent = idx === currentStageIndex
            const Icon = stage.icon

            return (
              <li
                key={stage.id}
                className={`flex items-start gap-3 rounded-xl p-2.5 transition-colors ${
                  isCurrent
                    ? "bg-primary/10 border border-primary/20"
                    : isCompleted
                    ? "text-muted-foreground/80 opacity-75"
                    : "opacity-40"
                }`}
              >
                <div
                  className={`mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                    isCompleted
                      ? "bg-emerald-500 text-white"
                      : isCurrent
                      ? "bg-primary text-primary-foreground animate-pulse"
                      : "border border-border text-muted-foreground"
                  }`}
                >
                  {isCompleted ? "✓" : stage.id}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-semibold ${isCurrent ? "text-primary" : "text-foreground"}`}>
                      {stage.title}
                    </span>
                    {isCurrent && (
                      <Loader2 className="size-3 animate-spin text-primary" />
                    )}
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed mt-0.5">
                    {stage.subtitle}
                  </p>
                </div>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
