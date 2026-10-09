"use client"

import { ShoppingCart, ExternalLink, ShieldCheck, Tag, Star } from "lucide-react"

interface RetailerPriceMatrixCardProps {
  retailerPriceMatrix?: {
    query?: string
    has_data?: boolean
    typical_price_range?: string | null
    retailers?: Array<{
      store_name?: string
      domain?: string
      price?: string
      extracted_price?: number | null
      link?: string
      rating?: number
      reviews?: number
      delivery?: string
      thumbnail?: string
      is_authorized?: boolean
      badge?: string | null
    }>
  }
}

export function RetailerPriceMatrixCard({ retailerPriceMatrix }: RetailerPriceMatrixCardProps) {
  if (!retailerPriceMatrix || !retailerPriceMatrix.has_data || !retailerPriceMatrix.retailers?.length) {
    return null
  }

  const { typical_price_range, retailers } = retailerPriceMatrix

  return (
    <div className="rounded-xl border border-border bg-card p-4 transition-all">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/50 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded bg-primary/10 p-1 text-primary">
            <ShoppingCart className="size-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              Authorized Retailer Price Matrix & MSRP Benchmark
            </h3>
            <p className="text-[11px] text-muted-foreground">
              Cross-checked retail distribution pricing across major authorized channels.
            </p>
          </div>
        </div>
        <span className="rounded bg-muted px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
          SerpApi Google Shopping
        </span>
      </div>

      {typical_price_range && (
        <div className="mt-3 flex items-center justify-between rounded-lg border border-primary/20 bg-primary/5 p-2.5 text-xs text-foreground/90">
          <div className="flex items-center gap-1.5 font-medium">
            <Tag className="size-3.5 text-primary" />
            <span>Observed Market MSRP Range:</span>
          </div>
          <span className="font-mono font-semibold text-primary">{typical_price_range}</span>
        </div>
      )}

      <div className="mt-3 grid gap-2.5 sm:grid-cols-2 md:grid-cols-3">
        {retailers.slice(0, 6).map((store, idx) => (
          <div
            key={idx}
            className="flex flex-col justify-between rounded-lg border border-border/70 bg-background/60 p-3 transition-all hover:border-primary/40"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <span className="truncate text-xs font-semibold text-foreground">
                  {store.store_name}
                </span>
                {store.is_authorized && (
                  <span className="inline-flex shrink-0 items-center gap-0.5 rounded-full bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-medium text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    <ShieldCheck className="size-2.5" /> Authorized
                  </span>
                )}
              </div>

              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-base font-bold tracking-tight text-foreground">
                  {store.price || "Check Store"}
                </span>
                {store.badge && (
                  <span className="text-[10px] text-muted-foreground font-medium">
                    {store.badge}
                  </span>
                )}
              </div>

              {(store.rating || store.delivery) && (
                <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                  {store.rating && (
                    <span className="inline-flex items-center gap-0.5 text-amber-500">
                      <Star className="size-3 fill-amber-500" />
                      <span className="font-medium text-foreground">{store.rating}</span>
                      {store.reviews && <span>({store.reviews})</span>}
                    </span>
                  )}
                  {store.delivery && (
                    <span className="truncate max-w-[120px]">{store.delivery}</span>
                  )}
                </div>
              )}
            </div>

            {store.link && (
              <a
                href={store.link}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-flex items-center justify-center gap-1 rounded-md border border-border bg-muted/40 py-1 text-xs font-medium text-foreground hover:bg-muted transition-colors"
              >
                Inspect Listing <ExternalLink className="size-3 text-muted-foreground" />
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
