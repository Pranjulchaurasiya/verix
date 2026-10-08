import { SiteHeader } from "@/components/site-header"
import { WebhookTester } from "@/components/webhook-tester"

export default function IntegrationsPage() {
  return (
    <div className="min-h-svh bg-background">
      <SiteHeader />
      <main className="mx-auto max-w-4xl space-y-8 px-4 py-10">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Integrations & Webhooks</h1>
          <p className="mt-2 text-muted-foreground">
            Connect Verix real-time threat intelligence directly to your security stack, ERP, or marketplace monitoring bot.
          </p>
        </div>

        {/* Live Webhook Tester Component */}
        <WebhookTester />

        <div>
          <h2 className="text-xl font-semibold tracking-tight mb-4">Supported Adapters & Connectors</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              ["Webhook Alerts", "Live Engine", "Real-time enterprise dispatching with HMAC-SHA256 signatures, replay attack rejection, and configurable event filters for high-risk scans."],
              ["Scan API", "Adapter implemented", "The Check page supports multipart image and URL requests to the existing FastAPI backend. Configure the API origin and CORS to connect it."],
              ["Audit Merkle CLI", "CLI Tool Ready", "Offline cryptographic verification tool for RFC 8032 Ed25519 signatures and Merkle proof validation without network dependencies."],
              ["DMCA & VeRO Desk", "Integrated", "One-click statutory takedown dossier generation for Amazon Brand Registry, eBay VeRO, Shopify Trust & Safety, and Google Copyright."],
              ["Claude / Gemini", "Planned", "Future AI agent connectors for automated multi-agent case investigation and visual provenance synthesis."],
              ["Browser extension", "Planned", "Future shortcut to inspect a listing or image from its source page with instant Lens reverse-search lookups."]
            ].map(([name, status, description]) => (
              <section key={name} className="rounded-2xl border border-border bg-card p-5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-semibold">{name}</h3>
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    status === "Live Engine" || status === "CLI Tool Ready" || status === "Integrated" || status === "Adapter implemented"
                      ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                      : "bg-secondary text-muted-foreground"
                  }`}>
                    {status}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{description}</p>
              </section>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

