"use client"

import { DollarSign, AlertTriangle, CheckCircle2, TrendingDown, Layers } from "lucide-react"

interface PricingDistributionCardProps {
  pricingAnalysis?: any
}

export function PricingDistributionCard({ pricingAnalysis }: PricingDistributionCardProps) {
  if (!pricingAnalysis || !pricingAnalysis.has_pricing_data || pricingAnalysis.sample_size < 2) {
    return null
  }

  const {
    sample_size,
    median_usd,
    mean_usd,
    iqr_usd,
    lower_bound_usd,
    upper_bound_usd,
    has_pricing_anomaly,
    severe_discount_detected,
    outlier_count,
    anomaly_summary,
    priced_listings = []
  } = pricingAnalysis

  const currSym = pricingAnalysis.currency_symbol || "$"
  const currCode = pricingAnalysis.display_currency || "USD"
  const isINR = currCode === "INR"

  const formatPrice = (val?: number | null) => {
    if (val === undefined || val === null) return "—"
    return `${currSym}${Number(val).toLocaleString()}`
  }

  const medianDisp = pricingAnalysis.median_display ?? median_usd
  const iqrDisp = pricingAnalysis.iqr_display ?? iqr_usd
  const lowerDisp = pricingAnalysis.lower_bound_display ?? lower_bound_usd
  const upperDisp = pricingAnalysis.upper_bound_display ?? upper_bound_usd

  return (
    <section className="rounded-xl border border-border bg-card p-4 space-y-3" aria-label="Pricing Distribution">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <DollarSign className="size-4 text-emerald-500" />
          <h3 className="text-sm font-semibold">Multi-Retailer Pricing Dispersion & Outlier Analysis</h3>
          <span className="rounded bg-muted px-2 py-0.5 text-xs text-muted-foreground font-mono">
            {sample_size} prices sampled
          </span>
        </div>
        {severe_discount_detected ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-semibold text-red-500">
            <AlertTriangle className="size-3" /> Counterfeit Pricing Anomaly
          </span>
        ) : has_pricing_anomaly ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-500">
            <TrendingDown className="size-3" /> Price Outliers Detected
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-500">
            <CheckCircle2 className="size-3" /> Normal Market Distribution
          </span>
        )}
      </div>

      {/* Benchmark Metric Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
        <div className="rounded-lg border border-border bg-muted/40 p-2.5">
          <span className="text-muted-foreground">Market Median</span>
          <p className="mt-0.5 text-base font-bold text-foreground font-mono">
            {formatPrice(medianDisp)} <span className="text-[10px] font-normal text-muted-foreground">{currCode}</span>
          </p>
          {isINR && median_usd && (
            <span className="text-[10px] font-mono text-muted-foreground/80">(${median_usd} USD)</span>
          )}
        </div>
        <div className="rounded-lg border border-border bg-muted/40 p-2.5">
          <span className="text-muted-foreground">Interquartile Range (IQR)</span>
          <p className="mt-0.5 text-base font-bold text-foreground font-mono">
            {formatPrice(iqrDisp)}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-muted/40 p-2.5">
          <span className="text-muted-foreground">Lower Fence (IQR - 1.5)</span>
          <p className="mt-0.5 text-base font-bold text-foreground font-mono">
            {formatPrice(lowerDisp)}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-muted/40 p-2.5">
          <span className="text-muted-foreground">Upper Fence (IQR + 1.5)</span>
          <p className="mt-0.5 text-base font-bold text-foreground font-mono">
            {formatPrice(upperDisp)}
          </p>
        </div>
      </div>

      {/* Anomaly summary text */}
      <p className="text-xs leading-relaxed text-muted-foreground">
        {anomaly_summary}
      </p>

      {/* Listing comparison items */}
      {priced_listings.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Retail Price Comparison ({priced_listings.length})
          </span>
          <div className="grid gap-1.5 max-h-48 overflow-y-auto">
            {priced_listings.map((p: any, idx: number) => (
              <div
                key={idx}
                className={`flex items-center justify-between rounded-lg border px-3 py-1.5 text-xs ${
                  p.is_outlier
                    ? p.anomaly_type === "severe_discount_counterfeit_risk"
                      ? "border-red-500/30 bg-red-500/5 text-red-500"
                      : "border-amber-500/30 bg-amber-500/5 text-amber-500"
                    : "border-border bg-card text-foreground"
                }`}
              >
                <div className="flex items-center gap-2 truncate max-w-[65%]">
                  <span className="font-semibold">{p.domain}</span>
                  {p.is_outlier && (
                    <span className="rounded bg-red-500/10 px-1.5 py-0.2 text-[10px] font-bold uppercase">
                      {p.anomaly_type === "severe_discount_counterfeit_risk" ? "Bait & Switch Risk" : "Outlier"}
                    </span>
                  )}
                </div>
                <div className="text-right font-mono text-xs">
                  <span className="font-bold">
                    {p.display_price !== undefined
                      ? `${currSym}${Number(p.display_price).toLocaleString()} ${currCode}`
                      : `$${p.usd_price} USD`}
                  </span>
                  {isINR && p.usd_price && (
                    <span className="ml-1 text-[10px] text-muted-foreground font-normal">
                      (${p.usd_price})
                    </span>
                  )}
                  {p.modified_z_score !== undefined && (
                    <span className="ml-2 text-[10px] text-muted-foreground">
                      Z: {p.modified_z_score > 0 ? `+${p.modified_z_score}` : p.modified_z_score}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
