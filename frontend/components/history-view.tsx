"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { History, Trash2, Search } from "lucide-react"
import type { CheckResult } from "@/lib/types"
import { useHistory, clearHistory, removeCheck } from "@/lib/history-store"
import { timeAgo } from "@/lib/verdict-meta"
import { VerdictBadge } from "@/components/verdict-badge"
import { ResultView } from "@/components/result-view"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"
import { deleteScan, fetchScanById, fetchScanHistory, mapSavedScanResponse } from "@/lib/scan-service"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export function HistoryView({ compact = false }: { compact?: boolean }) {
  const demoHistory = useHistory()
  const [connectedHistory, setConnectedHistory] = useState<CheckResult[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState("")
  const [deleting, setDeleting] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    async function load() {
      try {
        const response = await fetchScanHistory(controller.signal) as { items?: Array<{ id?: string }> }
        const ids = Array.isArray(response.items) ? response.items.map(item => item.id).filter((id): id is string => typeof id === "string") : []
        const records = await Promise.allSettled(ids.map(id => fetchScanById(id, controller.signal)))
        if (controller.signal.aborted) return
        setConnectedHistory(records.filter((item): item is PromiseFulfilledResult<unknown> => item.status === "fulfilled").map(item => mapSavedScanResponse(item.value)))
        setLoadError(records.some(item => item.status === "rejected") ? "Some saved checks could not be loaded." : "")
      } catch {
        if (!controller.signal.aborted) setLoadError("Connected history is unavailable. Your demo cases are still shown.")
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    void load()
    return () => controller.abort()
  }, [])
  const allHistory = [...connectedHistory, ...demoHistory]
  const history = Array.from(new Map(allHistory.map(item => [item.id, item])).values()).sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt))
  const [query, setQuery] = useState("")
  const filtered = history.filter(item => [item.sourceUrl, item.verdict, item.persona, item.explanation, ...item.matches.map(m => `${m.domain} ${m.title}`)].join(" ").toLowerCase().includes(query.toLowerCase()))
  const visible = compact ? filtered.slice(0, 3) : filtered
  const [active, setActive] = useState<CheckResult | null>(null)

  if (history.length === 0) {
    return (
      <div className={compact ? "history-empty" : "flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card px-6 py-6 text-center"}>
        <span className="flex size-11 items-center justify-center rounded-full bg-secondary text-muted-foreground">
          <History className="size-5" />
        </span>
        <h2 className="mt-4 text-base font-medium">{loading ? "Loading checks…" : "No checks yet"}</h2>
        {loadError && <p role="alert" className="mt-1 text-sm text-caution">{loadError}</p>}
        <p className="mt-1 max-w-xs text-sm text-muted-foreground">
          Photos you check will show up here so you can revisit the results anytime.
        </p>
        {!compact && <Button
          className="mt-5 gap-1.5"
          render={
            <Link href="/">
              <Search className="size-4" /> Run your first check
            </Link>
          }
        />}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {loadError && <p role="alert" className="text-sm text-caution">{loadError}</p>}
      {!compact && <Input aria-label="Search investigations" placeholder="Search by domain, verdict or product…" value={query} onChange={e => setQuery(e.target.value)} />}
      {compact && <Link href="/history" className="text-sm text-primary underline">View all investigations</Link>}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {history.length} recent {history.length === 1 ? "check" : "checks"} · connected and demo
        </p>
        {!compact && <Button variant="ghost" size="sm" disabled={deleting} onClick={async () => {
          setDeleting(true)
          const outcomes = await Promise.allSettled(connectedHistory.map(item => deleteScan(item.id)))
          const failed = new Set(outcomes.flatMap((outcome, index) => outcome.status === "rejected" ? [connectedHistory[index].id] : []))
          setConnectedHistory(items => items.filter(item => failed.has(item.id)))
          try { clearHistory() } catch { toast.error("Demo history could not be cleared from this device.") }
          if (failed.size) toast.error(`${failed.size} connected checks could not be deleted. Retry.`)
          setDeleting(false)
        }} className="gap-1.5 text-muted-foreground">
          <Trash2 className="size-4" /> Clear all
        </Button>}
      </div>

      <Dialog open={!!active} onOpenChange={(o) => !o && setActive(null)}>
        <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {visible.map((item) => (
            <li key={item.id}>
              <DialogTrigger
                  onClick={() => setActive(item)}
                  className="flex w-full items-center gap-3 rounded-xl border border-border bg-card p-3 text-left transition-colors hover:bg-secondary/50"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={item.imageUrl || "/placeholder.svg"}
                    alt="Checked product"
                    className="size-12 shrink-0 rounded-lg border border-border object-cover"
                  />
                  <div className="min-w-0 flex-1">
                    <VerdictBadge verdict={item.verdict} />
                    <p className="mt-1.5 truncate text-xs text-muted-foreground">
                      {item.matches.length} {item.matches.length === 1 ? "source" : "sources"} · {timeAgo(item.createdAt)}
                    </p>
                  </div>
                  {item.trustScore !== null && (
                    <span className="shrink-0 text-lg font-semibold tabular-nums text-muted-foreground">
                      {item.trustScore}
                    </span>
                  )}
              </DialogTrigger>
            </li>
          ))}
        </ul>
        {visible.length === 0 && <p role="status" className="text-sm text-muted-foreground">No investigations match this search.</p>}

        <DialogContent className="max-h-[85svh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Check details</DialogTitle>
          </DialogHeader>
          {active && (
            <>
              <ResultView result={active} />
              <Button
                variant="outline"
                size="sm"
                onClick={async () => {
                  try {
                    if (!active.demo) await deleteScan(active.id)
                    if (active.demo) removeCheck(active.id)
                    else setConnectedHistory(items => items.filter(item => item.id !== active.id))
                    setActive(null)
                  } catch {
                    toast.error("The connected scan could not be deleted. Please retry.")
                  }
                }}
                className="gap-1.5"
              >
                <Trash2 className="size-4" /> Remove from history
              </Button>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
