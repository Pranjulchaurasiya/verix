import { BadgeCheck, TriangleAlert, ExternalLink, Globe, ChevronDown } from "lucide-react"
import { useState } from "react"
import type { ImageMatch } from "@/lib/types"
import { formatPrice } from "@/lib/verdict-meta"
import { cn } from "@/lib/utils"

export function MatchList({ matches, currency }: { matches: ImageMatch[]; currency?: string }) {
  const [expanded, setExpanded] = useState<number | null>(null)
  if (matches.length === 0) {
    return <p className="text-sm text-muted-foreground">No other appearances of this photo were found.</p>
  }

  return (
    <ul className="divide-y divide-border rounded-xl border border-border bg-card">
      {matches.map((m, i) => (
        <li key={`${m.domain}-${i}`} className="p-3">
          <button type="button" onClick={() => setExpanded(expanded === i ? null : i)} className="flex w-full items-center gap-3 text-left">
          <div className="relative size-11 shrink-0 overflow-hidden rounded-lg border border-border bg-muted/30">
            {m.thumbnail ? (
              /* eslint-disable-next-line @next/next/no-img-element */
              <img
                src={m.thumbnail}
                alt={m.title || m.domain}
                className="size-full object-cover"
                loading="lazy"
                onError={(e) => {
                  (e.currentTarget as HTMLElement).style.display = "none"
                }}
              />
            ) : (
              <span
                className={cn(
                  "flex size-full items-center justify-center",
                  m.whitelisted
                    ? "bg-trusted/10 text-trusted"
                    : m.flagged
                      ? "bg-risk/10 text-risk"
                      : "bg-secondary text-muted-foreground",
                )}
              >
                {m.sourceIcon ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img src={m.sourceIcon} alt="" className="size-5 rounded-sm object-contain" />
                ) : m.whitelisted ? (
                  <BadgeCheck className="size-5" />
                ) : m.flagged ? (
                  <TriangleAlert className="size-5" />
                ) : (
                  <Globe className="size-5" />
                )}
              </span>
            )}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="truncate text-sm font-medium">{m.domain}</span>
              {m.whitelisted && (
                <span className="rounded-full bg-trusted/10 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-trusted">
                  Known host
                </span>
              )}
              {m.flagged && !m.whitelisted && (
                <span className="rounded-full bg-risk/10 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-risk">
                  Flagged
                </span>
              )}
              {!m.whitelisted && !m.flagged && m.legitimacyLabel && (
                <span className="rounded-full bg-secondary px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                  {m.legitimacyLabel}
                </span>
              )}
            </div>
            <p className="truncate text-xs text-muted-foreground">{m.title}</p>
          </div>

          <div className="flex shrink-0 items-center gap-3">
            {typeof m.price === "number" && (
              <span className="text-sm font-semibold tabular-nums">{formatPrice(m.price, m.currency || currency)}</span>
            )}
            {/^https?:\/\//i.test(m.url) && <a
              href={m.url}
              target="_blank"
              rel="noopener noreferrer nofollow"
              className="text-muted-foreground transition-colors hover:text-foreground"
              aria-label={`Open ${m.domain} in a new tab`}
              onClick={(event) => event.stopPropagation()}
            >
              <ExternalLink className="size-4" />
            </a>}
            <ChevronDown className={cn("size-4 text-muted-foreground transition-transform", expanded === i && "rotate-180")} />
          </div>
          </button>
          {expanded === i && <div className="mt-3 ml-11 grid gap-2 rounded-lg bg-secondary/40 p-3 text-xs text-muted-foreground sm:grid-cols-3">
            <span><strong className="text-foreground">Engine:</strong> {m.engine || "Google Lens"}</span>
            <span><strong className="text-foreground">Evidence:</strong> {(m.evidenceType || "visual match").replaceAll("_", " ")}</span>
            <span><strong className="text-foreground">Corroboration:</strong> {m.corroborationCount && m.corroborationCount > 1 ? `${m.corroborationCount} engine signals` : "1 engine signal"}</span>
            <span><strong className="text-foreground">Assessment:</strong> {m.legitimacyLabel || (m.flagged ? "Risk signal" : m.whitelisted ? "Trusted platform" : "Unverified source")}{typeof m.legitimacyScore === "number" ? ` · ${m.legitimacyScore}/100` : ""}</span>
            {m.observedAt && !Number.isNaN(Date.parse(m.observedAt)) && <span className="sm:col-span-3"><strong className="text-foreground">Retrieved:</strong> {new Date(m.observedAt).toLocaleString()} · page status may have changed</span>}
            {m.legitimacyReasons?.map((reason) => <span key={reason} className="sm:col-span-3">• {reason}</span>)}
            {/^https?:\/\//i.test(m.url) && <a className="font-medium text-primary hover:underline sm:col-span-3" href={m.url} target="_blank" rel="noopener noreferrer nofollow">Open source listing in a new tab →</a>}
          </div>}
        </li>
      ))}
    </ul>
  )
}
