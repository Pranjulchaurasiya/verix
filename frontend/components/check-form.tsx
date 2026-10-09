"use client"

import { useCallback, useMemo, useRef, useState } from "react"
import { Link2, Upload, Search, ImageIcon, X, Layers, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import type { InputType, Persona } from "@/lib/types"
import { cn } from "@/lib/utils"

export interface SubmitPayload {
  file?: File
  inputType: InputType
  imageUrl: string
  sourceUrl?: string
  seed: string
}

const EXAMPLES = [
  { label: "Suspicious sneaker deal", src: "/demo/sneaker.png", seed: "example-sneaker" },
  { label: "Designer handbag", src: "/demo/handbag.png", seed: "example-handbag" },
  { label: "Insufficient evidence", src: "/demo/sneaker.png", seed: "example-insufficient" },
  { label: "Cached evidence", src: "/demo/sneaker.png", seed: "example-sneaker-cached" },
]

export function CheckForm({
  persona,
  disabled,
  onSubmit,
  onBatchSubmit,
}: {
  persona: Persona
  disabled?: boolean
  onSubmit: (payload: SubmitPayload) => void
  onBatchSubmit?: (items: { url: string; label?: string }[]) => void
}) {
  const [tab, setTab] = useState<InputType>("url")
  const [url, setUrl] = useState("")
  const [batchText, setBatchText] = useState("")
  const [preview, setPreview] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const [seed, setSeed] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState<File>()
  const [error, setError] = useState("")
  const fileRef = useRef<HTMLInputElement>(null)

  const urlPlaceholder =
    persona === "buyer"
      ? "Paste a listing link or image URL"
      : "Paste the URL of your product photo"

  const urlPreview = useMemo(() => {
    const trimmed = url.trim()
    if (!trimmed || !trimmed.startsWith("http")) return null
    try {
      const parsed = new URL(trimmed)
      const hostname = parsed.hostname.replace(/^www\./, "").toLowerCase()

      // Direct image URL
      if (/\.(png|jpe?g|webp|gif|avif)(\?.*)?$/i.test(trimmed)) {
        return {
          imageUrl: trimmed,
          domain: hostname,
          label: "Direct Image Link",
          type: "direct_image" as const,
        }
      }

      // Amazon ASIN URL
      const asinMatch = trimmed.match(/(?:\/dp\/|\/gp\/product\/|\/gp\/aw\/d\/|\/d\/|\/product\/|\/gp\/offer-listing\/|[?&]asin=)([A-Z0-9]{10})/i)
      if (asinMatch && (hostname.includes("amazon.") || hostname.includes("amzn."))) {
        const asin = asinMatch[1].toUpperCase()
        return {
          imageUrl: `https://images-na.ssl-images-amazon.com/images/P/${asin}.01.MAIN._SCRM_.jpg`,
          domain: hostname,
          label: `Amazon Official Catalog (ASIN: ${asin})`,
          type: "amazon" as const,
        }
      }

      // Recognized or general domain
      return {
        domain: hostname,
        label: `${hostname.split(".")[0].toUpperCase()} Product Page`,
        type: "marketplace" as const,
      }
    } catch {
      return null
    }
  }, [url])

  const handleFile = useCallback((file: File) => {
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type) || file.size > 10 * 1024 * 1024) { setError("Choose a JPG, PNG or WebP image up to 10 MB."); return }
    setError("")
    setFile(file)
    const reader = new FileReader()
    reader.onload = () => {
      setPreview(reader.result as string)
      setFileName(file.name)
      setSeed(`${file.name}-${file.size}`)
    }
    reader.readAsDataURL(file)
    reader.onerror = () => setError("Could not read this image. Choose another file.")
  }, [])

  const clearFile = () => {
    setPreview(null)
    setFile(undefined)
    setFileName(null)
    setSeed(null)
    if (fileRef.current) fileRef.current.value = ""
  }

  const submit = () => {
    if (tab === "batch") {
      const lines = batchText.split("\n").map(l => l.trim()).filter(Boolean)
      const items = lines.map(line => {
        const parts = line.split("#")
        const u = parts[0].trim()
        const lbl = parts[1]?.trim()
        return { url: u, label: lbl }
      }).filter(it => it.url.startsWith("http"))
      if (items.length === 0) {
        setError("Enter at least one valid HTTP/HTTPS URL.")
        return
      }
      setError("")
      if (onBatchSubmit) {
        onBatchSubmit(items)
      }
    } else if (tab === "url") {
      const trimmed = url.trim()
      if (!trimmed) return
      try { if (!["http:", "https:"].includes(new URL(trimmed).protocol)) throw new Error() } catch { setError("Enter a complete http or https listing URL."); return }
      setError("")
      const isImage = /\.(png|jpe?g|webp|gif|avif)(\?.*)?$/i.test(trimmed)
      onSubmit({
        inputType: "url",
        imageUrl: urlPreview?.imageUrl || (isImage ? trimmed : "/demo/link-preview.png"),
        sourceUrl: trimmed,
        seed: trimmed,
      })
    } else if (preview && seed) {
      onSubmit({ inputType: "upload", imageUrl: preview, seed, file })
    }
  }

  const canSubmit = tab === "batch" ? batchText.trim().length > 10 : tab === "url" ? url.trim().length > 3 : Boolean(preview)

  return (
    <div className="check-form space-y-5">
      {error && <p role="alert" className="text-sm text-risk">{error}</p>}
      <Tabs value={tab} onValueChange={(v) => setTab(v as InputType)}>
        <TabsList className="input-tabs h-11 w-full rounded-none bg-transparent p-0">
          <TabsTrigger value="url" className="flex-1 gap-1.5">
            <Link2 className="size-3.5" /> Paste a link
          </TabsTrigger>
          <TabsTrigger value="upload" className="flex-1 gap-1.5">
            <Upload className="size-3.5" /> Upload a photo
          </TabsTrigger>
          <TabsTrigger value="batch" className="flex-1 gap-1.5">
            <Layers className="size-3.5" /> Multi-Image Batch
          </TabsTrigger>
        </TabsList>

        <TabsContent value="url" className="mt-5">
          <label htmlFor="listing-url" className="mb-2 block text-sm text-muted-foreground">Product listing or image URL</label>
          <div className="flex flex-col gap-3">
            <Input
              id="listing-url"
              type="url"
              aria-label="Product listing or image URL"
              inputMode="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder={urlPlaceholder}
              disabled={disabled}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.nativeEvent.isComposing && canSubmit) submit()
              }}
              className="h-14 rounded-lg border-border bg-background/70 px-4 text-base"
            />

            {urlPreview && (
              <div className="flex items-center gap-3 rounded-xl border border-primary/20 bg-primary/5 p-3 animate-in fade-in-50 duration-200">
                {urlPreview.imageUrl ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={urlPreview.imageUrl}
                    alt="Product preview"
                    className="size-14 shrink-0 rounded-lg border border-border object-cover bg-background"
                    onError={(e) => {
                      (e.currentTarget as HTMLElement).style.display = "none"
                    }}
                  />
                ) : (
                  <span className="flex size-14 shrink-0 items-center justify-center rounded-lg border border-border bg-background text-muted-foreground">
                    <ImageIcon className="size-6" />
                  </span>
                )}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-semibold text-primary">{urlPreview.domain}</span>
                    <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">Recognized</span>
                  </div>
                  <p className="truncate text-xs font-medium text-foreground mt-0.5">{urlPreview.label}</p>
                  <p className="text-[11px] text-muted-foreground">
                    {urlPreview.imageUrl
                      ? "High-resolution product photo preview resolved · ready to investigate"
                      : "Listing recognized · Verix will extract the primary product photo automatically upon inspection"}
                  </p>
                </div>
              </div>
            )}

            <Button onClick={submit} disabled={disabled || !canSubmit} className="analyze-button h-12 gap-2 rounded-lg px-5">
              <Search className="size-4" /> Investigate image
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="upload" className="mt-3">
          {preview ? (
            <div className="flex items-center gap-3 rounded-xl border border-border bg-card p-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={preview || "/placeholder.svg"} alt="Selected preview" className="size-14 rounded-lg object-cover" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{fileName}</p>
                <p className="text-xs text-muted-foreground">Ready to check</p>
              </div>
              <Button variant="ghost" size="icon" onClick={clearFile} aria-label="Remove photo">
                <X className="size-4" />
              </Button>
              <Button onClick={submit} disabled={disabled} className="h-9 gap-1.5">
                <Search className="size-4" /> Analyze
              </Button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault()
                setDragging(false)
                const file = e.dataTransfer.files?.[0]
                if (file?.type.startsWith("image/")) handleFile(file)
              }}
              className={cn(
                "flex w-full flex-col items-center justify-center gap-2 rounded-2xl border border-dashed p-10 text-center transition-colors",
                dragging ? "border-primary bg-primary/5" : "border-border bg-card hover:bg-secondary/40",
              )}
            >
              <span className="flex size-10 items-center justify-center rounded-full bg-secondary text-muted-foreground">
                <ImageIcon className="size-5" />
              </span>
              <span className="text-sm font-medium">Drop an image or click to browse</span>
              <span className="text-xs text-muted-foreground">PNG, JPG or WebP</span>
            </button>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFile(file)
            }}
          />
        </TabsContent>

        <TabsContent value="batch" className="mt-4 space-y-3">
          <div className="flex items-center justify-between">
            <label htmlFor="batch-urls" className="text-sm text-muted-foreground">
              Multi-angle product URLs (1 per line, optional #label)
            </label>
            <button
              type="button"
              onClick={() => {
                setBatchText(
                  "https://www.amazon.in/dp/B08L5WHJ2T # Front Angle\n" +
                  "https://www.flipkart.com/shoes/p/itm123 # Packaging & Tag\n" +
                  "https://www.meesho.com/s/p/abc # Seller Listing"
                )
              }}
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              <Sparkles className="size-3" /> Load sample batch
            </button>
          </div>
          <textarea
            id="batch-urls"
            rows={4}
            value={batchText}
            onChange={(e) => setBatchText(e.target.value)}
            placeholder={"https://example.com/photo-front.jpg # Front Angle\nhttps://example.com/photo-label.jpg # Packaging\nhttps://example.com/box.jpg # Tag"}
            className="w-full rounded-lg border border-border bg-background/70 p-3 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-primary"
            disabled={disabled}
          />
          <p className="text-xs text-muted-foreground">
            Scans up to 10 product images concurrently with rate limiting & deduplication.
          </p>
          <Button onClick={submit} disabled={disabled || !canSubmit} className="analyze-button h-12 w-full gap-2 rounded-lg px-5">
            <Layers className="size-4" /> Run Concurrent Batch Scan
          </Button>
        </TabsContent>
      </Tabs>

      <details className="demo-examples">
        <summary>Preview with a sample investigation <span>4 examples</span></summary>
        <div className="mt-3 flex flex-wrap gap-2">{EXAMPLES.map((ex) => (
          <button
            key={ex.seed}
            type="button"
            disabled={disabled}
            onClick={() =>
              onSubmit({ inputType: "upload", imageUrl: ex.src, seed: ex.seed })
            }
            className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-3 py-2 text-sm text-foreground transition-colors hover:bg-secondary disabled:opacity-50"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={ex.src || "/placeholder.svg"} alt="" className="size-4 rounded-full object-cover" />
            {ex.label}
          </button>
        ))}</div>
      </details>
    </div>
  )
}
