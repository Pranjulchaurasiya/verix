import type { Verdict } from "./types"

export interface VerdictMeta {
  label: string
  /** Short line shown under the label */
  tagline: string
  /** Semantic token name used for accents (maps to CSS vars) */
  tone: "safe" | "caution" | "risk" | "trusted" | "muted"
}

export const VERDICT_META: Record<Verdict, VerdictMeta> = {
  moderate_risk: { label: "Review suggested", tagline: "Mixed public signals", tone: "caution" },
  trusted: {
    label: "Recognized platform host",
    tagline: "Seller and item still need checking",
    tone: "trusted",
  },
  low_risk: {
    label: "Few web risk signals",
    tagline: "Seller and item still need checking",
    tone: "safe",
  },
  high_risk: {
    label: "High risk signals",
    tagline: "Worth weighing carefully",
    tone: "risk",
  },
  insufficient_data: {
    label: "Insufficient data",
    tagline: "Not enough to judge yet",
    tone: "muted",
  },
}

export function toneClasses(tone: VerdictMeta["tone"]): {
  text: string
  bg: string
  border: string
  ring: string
} {
  switch (tone) {
    case "trusted":
      return {
        text: "text-trusted",
        bg: "bg-trusted/10",
        border: "border-trusted/25",
        ring: "text-trusted",
      }
    case "safe":
      return {
        text: "text-safe",
        bg: "bg-safe/10",
        border: "border-safe/25",
        ring: "text-safe",
      }
    case "caution":
      return {
        text: "text-caution",
        bg: "bg-caution/15",
        border: "border-caution/30",
        ring: "text-caution",
      }
    case "risk":
      return {
        text: "text-risk",
        bg: "bg-risk/10",
        border: "border-risk/25",
        ring: "text-risk",
      }
    default:
      return {
        text: "text-muted-foreground",
        bg: "bg-muted",
        border: "border-border",
        ring: "text-muted-foreground",
      }
  }
}

export function formatPrice(price: number, currency = "INR"): string {
  try {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(price)
  } catch {
    return `₹${price.toLocaleString("en-IN")}`
  }
}

export function timeAgo(iso: string): string {
  const then = new Date(iso).getTime()
  const secs = Math.max(1, Math.round((Date.now() - then) / 1000))
  if (secs < 60) return `${secs}s ago`
  const mins = Math.round(secs / 60)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.round(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.round(hrs / 24)
  return `${days}d ago`
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  })
}
