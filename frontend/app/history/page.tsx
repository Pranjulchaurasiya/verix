import { SiteHeader } from "@/components/site-header"
import { HistoryView } from "@/components/history-view"

export default function HistoryPage() {
  return (
    <div className="min-h-svh bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl px-4 py-8 sm:py-12">
        <div className="mb-6 space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Check history</h1>
          <p className="text-sm text-muted-foreground">
            Connected checks are retrieved from your browser&apos;s scoped history. Demo cases stay on this device.
          </p>
        </div>
        <HistoryView />
      </main>
    </div>
  )
}
