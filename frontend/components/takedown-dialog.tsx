"use client"

import { useState } from "react"
import { ShieldAlert, Copy, Check, Download, ExternalLink, X, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"

interface TakedownDialogProps {
  scanId: string
  isOpen: boolean
  onClose: () => void
  demo?: boolean
}

export function TakedownDialog({ scanId, isOpen, onClose, demo }: TakedownDialogProps) {
  const [copied, setCopied] = useState(false)
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const loadNotice = async () => {
    if (data) return
    setLoading(true)
    try {
      if (demo) {
        setData({
          case_id: "VERIX-DEMO-2026",
          claimant_name: "Original Merchant / Catalog Rights Owner",
          infringing_count: 2,
          infringing_items: [
            { domain: "replica-outlet-deals.com", url: "https://replica-outlet-deals.com/item/1029" },
            { domain: "unauthorized-discount.net", url: "https://unauthorized-discount.net/p/shoe" }
          ],
          notice_text: `NOTICE OF COPYRIGHT INFRINGEMENT AND DEMAND FOR EXPEDITIOUS REMOVAL\nPursuant to 17 U.S.C. § 512(c) (DMCA) / Platform VeRO Guidelines\n\nCase Evidence ID: VERIX-DEMO-2026\nClaimant: Original Merchant / Catalog Rights Owner\nDigital Evidence: SerpApi reverse-image matches confirmed reproduction of original catalog media.\n\nInfringing URLs:\n  * replica-outlet-deals.com: https://replica-outlet-deals.com/item/1029\n  * unauthorized-discount.net: https://unauthorized-discount.net/p/shoe\n\nCryptographic Merkle Root: a8f5c...92d1\nEd25519 Evidence Signature: 3e7b...910a\n\nI have a good-faith belief that use of the material is unauthorized. Under penalty of perjury, I declare I am authorized to act on behalf of the copyright owner.`,
          platform_channels: {
            amazon: "https://brandregistry.amazon.com/brand-protection",
            ebay: "https://www.ebay.com/help/policies/member-behavior-policies/report-intellectual-property-infringements-vero?id=4349",
            google_dmca: "https://www.google.com/webmasters/tools/dmca-notice",
            shopify: "https://www.shopify.com/legal/dmca"
          }
        })
        return
      }

      const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "")
      const res = await fetch(`${base}/api/v1/enforce/takedown/${encodeURIComponent(scanId)}`)
      if (res.ok) {
        const pkg = await res.json()
        setData(pkg)
      } else {
        throw new Error("Could not generate notice.")
      }
    } catch {
      // Fallback
      setData({
        case_id: `VERIX-${scanId.slice(0, 8).toUpperCase()}`,
        notice_text: "Could not generate live notice. Please ensure scan details exist."
      })
    } finally {
      setLoading(false)
    }
  }

  if (isOpen && !data && !loading) {
    loadNotice()
  }

  if (!isOpen) return null

  const handleCopy = () => {
    if (data?.notice_text) {
      navigator.clipboard.writeText(data.notice_text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    if (!data?.notice_text) return
    const blob = new Blob([data.notice_text], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `DMCA_Takedown_${data.case_id || "Notice"}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="flex max-h-[90vh] w-full max-w-2xl flex-col rounded-2xl border border-border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-border p-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="size-5 text-amber-500" />
            <h2 className="text-lg font-bold">Seller Asset Protection & DMCA Notice</h2>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted">
            <X className="size-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-sm">
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-xs text-amber-700 dark:text-amber-400">
            <p className="font-semibold">Cryptographically Signed Takedown Package</p>
            <p className="mt-0.5">
              Case ID: <span className="font-mono font-bold">{data?.case_id || "Loading..."}</span> · Anchored with Ed25519 digital signature and Merkle inclusion proofs.
            </p>
          </div>

          <div>
            <span className="text-xs font-semibold text-muted-foreground uppercase">Statutory Notice Text</span>
            <pre className="mt-1.5 max-h-60 overflow-y-auto rounded-lg border border-border bg-muted/50 p-3 font-mono text-xs whitespace-pre-wrap text-foreground">
              {loading ? "Generating cryptographically anchored DMCA notice..." : data?.notice_text}
            </pre>
          </div>

          {data?.platform_channels && (
            <div>
              <span className="text-xs font-semibold text-muted-foreground uppercase">Direct Submission Channels</span>
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <a
                  href={data.platform_channels.amazon}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between rounded-lg border border-border p-2.5 hover:bg-muted"
                >
                  <span>Amazon Brand Registry</span>
                  <ExternalLink className="size-3 text-muted-foreground" />
                </a>
                <a
                  href={data.platform_channels.ebay}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between rounded-lg border border-border p-2.5 hover:bg-muted"
                >
                  <span>eBay VeRO Program</span>
                  <ExternalLink className="size-3 text-muted-foreground" />
                </a>
                <a
                  href={data.platform_channels.google_dmca}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between rounded-lg border border-border p-2.5 hover:bg-muted"
                >
                  <span>Google DMCA Removal</span>
                  <ExternalLink className="size-3 text-muted-foreground" />
                </a>
                <a
                  href={data.platform_channels.shopify}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between rounded-lg border border-border p-2.5 hover:bg-muted"
                >
                  <span>Shopify Takedown</span>
                  <ExternalLink className="size-3 text-muted-foreground" />
                </a>
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border p-4">
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleDownload} disabled={!data?.notice_text}>
              <Download className="mr-1.5 size-3.5" /> Download .txt
            </Button>
            <Button size="sm" onClick={handleCopy} disabled={!data?.notice_text}>
              {copied ? (
                <>
                  <Check className="mr-1.5 size-3.5 text-emerald-500" /> Copied!
                </>
              ) : (
                <>
                  <Copy className="mr-1.5 size-3.5" /> Copy Notice
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
