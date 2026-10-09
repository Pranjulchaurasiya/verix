import type { CheckResult, ImageMatch, Persona, Verdict, BatchScanResponse, BatchItemResult } from "./types"
import { analyzeImage } from "./mock-engine"
import type { SubmitPayload } from "@/components/check-form"
import { scopedApiFetch, getApiBaseUrl } from "./client-scope"

function safeUrl(value: unknown): string {
  if (typeof value !== "string") return ""
  try { const u = new URL(value); return ["http:", "https:"].includes(u.protocol) ? u.href : "" } catch { return "" }
}

function resolveMediaUrl(value: unknown): string {
  if (typeof value !== "string" || !value) return ""
  if (value.startsWith("http://") || value.startsWith("https://")) return value
  if (value.startsWith("/")) {
    const base = getApiBaseUrl()
    return `${base}${value}`
  }
  return value
}

export function mapScanResponse(raw: unknown, payload: SubmitPayload, persona: Persona): CheckResult {
  if (!raw || typeof raw !== "object") throw new Error("The server returned an invalid scan. Please retry.")
  const r = raw as Record<string, unknown>
  if (r.status === "failed" || typeof r.id !== "string" || typeof r.status !== "string") throw new Error("The server could not complete this scan. Please retry.")
  const text = (v: unknown, fallback = "") => typeof v === "string" ? v : fallback
  const matches: ImageMatch[] = (Array.isArray(r.matched_domains) ? r.matched_domains : []).filter(m => m && typeof m === "object").map(m => ({domain:text(m.domain, "Unknown source"), url:safeUrl(m.link), title:text(m.title, "Public image match"), price:typeof m.extracted_price === "number" && Number.isFinite(m.extracted_price) && m.extracted_price >= 0 ? m.extracted_price : undefined, currency:text(m.currency) || undefined, whitelisted:m.is_whitelisted === true, flagged:m.flagged === true, engine:text(m.engine) || undefined, evidenceType:text(m.evidence_type) || undefined, engines:Array.isArray(m.engines) ? m.engines.filter((v: unknown): v is string => typeof v === "string") : undefined, evidenceTypes:Array.isArray(m.evidence_types) ? m.evidence_types.filter((v: unknown): v is string => typeof v === "string") : undefined, corroborationCount:typeof m.corroboration_count === "number" ? m.corroboration_count : undefined, observedAt:text(m.observed_at) || undefined, legitimacyLabel:text(m.legitimacy_label) || undefined, legitimacyScore:typeof m.legitimacy_score === "number" ? m.legitimacy_score : undefined, legitimacyReasons:Array.isArray(m.legitimacy_reasons) ? m.legitimacy_reasons.filter((v: unknown): v is string => typeof v === "string") : undefined, sourceIcon:safeUrl(m.source_icon) || undefined, thumbnail:safeUrl(m.thumbnail) || undefined}))
  const bypass = r.is_whitelist_bypass === true || r.status === "trusted_whitelist"
  const insufficient = r.status === "insufficient_data" || r.risk_category === "insufficient_data" || (!bypass && matches.length < 2)
  const categories = ["trusted", "low_risk", "moderate_risk", "high_risk", "insufficient_data"]
  const verdict: Verdict = insufficient ? "insufficient_data" : bypass ? "trusted" : categories.includes(text(r.risk_category)) ? r.risk_category as Verdict : "insufficient_data"
  const createdAt = text(r.created_at, new Date().toISOString())
  const availability = ["in_stock", "out_of_stock", "discontinued"].includes(text(r.product_availability)) ? text(r.product_availability) as CheckResult["productAvailability"] : "unknown"
  const provenance = ["live_serpapi", "cached", "development_fallback"].includes(text(r.provenance)) ? text(r.provenance) as CheckResult["provenance"] : r.is_stale === true || r.status === "stale_cached" ? "cached" : "unknown"
  const aiOverview = text(r.ai_overview) || undefined
  const isSynthetic = r.is_synthetic === true
  const synthidDetected = r.synthid_detected === true
  const provenanceSummary = text(r.provenance_summary) || undefined
  const detectedGenerators = Array.isArray(r.detected_generators) ? r.detected_generators.filter((v: unknown): v is string => typeof v === "string") : []
  const pricingAnalysis = r.pricing_analysis
  const provenanceDetails = r.provenance_details
  return {id:r.id, createdAt, persona, inputType:payload.inputType, imageUrl:resolveMediaUrl(r.image_url) || payload.imageUrl, sourceUrl:payload.sourceUrl, verdict, trustScore:verdict === "insufficient_data" ? null : typeof r.trust_score === "number" && Number.isFinite(r.trust_score) ? Math.max(0, Math.min(100,r.trust_score)) : null, confidence:r.confidence === "high" || r.confidence === "medium" ? r.confidence : "low", explanation:text(r.explanation, "No explanation was returned. Review public matches independently."), recommendation:text(r.action_recommendation) || undefined, productAvailability:availability, provenance, aiOverview, isSynthetic, synthidDetected, provenanceSummary, detectedGenerators, pricingAnalysis, provenanceDetails, signals:bypass ? ["Trusted-platform bypass: deep risk analysis skipped"] : insufficient ? ["Fewer than two reliable public matches or insufficient assessment data; no score assigned"] : [], matches, currency:matches.find(m => m.currency)?.currency, degraded:r.is_stale === true || r.status === "stale_cached", lastVerifiedAt:text(r.stale_original_timestamp,createdAt), whitelistBypass:bypass, demo:false}
}

export async function scanProduct(payload: SubmitPayload, persona: Persona, mode: "demo" | "api"): Promise<CheckResult> {
  // Only intentional sample buttons may enter the simulator. Never turn a real
  // URL or user's uploaded image into a synthetic verdict under Demo mode.
  if (payload.seed.startsWith("example-")) { await new Promise(resolve => setTimeout(resolve, 1600)); return analyzeImage({...payload,persona}) }
  if (mode === "demo") throw new Error("This is a real product link, so Verix did not simulate a result. Select Connected API to analyze it, or use a sample investigation to preview Demo mode.")
  const body = new FormData()
  body.set("persona_mode", persona)
  if (payload.file) body.set("file",payload.file)
  else if (payload.sourceUrl) body.set("url",payload.sourceUrl)
  else throw new Error("Choose a photo or enter a listing URL.")
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 60000)
  try {
    const response = await scopedApiFetch("/api/v1/analyze", {method:"POST",body,signal:controller.signal})
    if (!response.ok) throw new Error(response.status === 429 ? "Too many requests. Wait a moment and retry." : response.status === 503 ? "Search is unavailable and no cached evidence was returned. Retry or select Demo mode." : `Scan failed (${response.status}). Check your input and retry.`)
    return mapScanResponse(await response.json(),payload,persona)
  } catch (error) {
    if (controller.signal.aborted) throw new Error("The scan timed out after 60 seconds. Retry or try the demo example.")
    if (error instanceof TypeError) throw new Error("Could not reach the scan API. Check the connection or select Demo mode.")
    throw error
  } finally { clearTimeout(timeout) }
}

/** API history access is prepared here; the current history UI remains local. */
export async function fetchScanHistory(signal?: AbortSignal): Promise<unknown> {
  const response = await scopedApiFetch("/api/v1/scans?limit=50", { signal })
  if (!response.ok) throw new Error("Could not load connected scan history. Please retry.")
  return response.json()
}

export async function fetchScanById(id: string, signal?: AbortSignal): Promise<unknown> {
  if (!id.trim()) throw new Error("A scan identifier is required.")
  const response = await scopedApiFetch(`/api/v1/scans/${encodeURIComponent(id)}`, { signal })
  if (!response.ok) throw new Error(response.status === 404 ? "This scan is unavailable for this browser." : "Could not load the scan. Please retry.")
  return response.json()
}

export function mapSavedScanResponse(raw: unknown): CheckResult {
  if (!raw || typeof raw !== "object") throw new Error("Invalid saved scan.")
  const scan = raw as Record<string, unknown>
  const persona: Persona = scan.persona_mode === "seller" ? "seller" : "buyer"
  const inputType = scan.input_type === "upload" ? "upload" : "url"
  return mapScanResponse(raw, {
    inputType,
    imageUrl: typeof scan.image_url === "string" ? scan.image_url : "",
    sourceUrl: typeof scan.source_url === "string" ? scan.source_url : undefined,
    seed: "saved-scan",
  }, persona)
}

export async function deleteScan(id: string): Promise<void> {
  if (!id.trim()) throw new Error("A scan identifier is required.")
  const response = await scopedApiFetch(`/api/v1/scans/${encodeURIComponent(id)}`, { method: "DELETE" })
  if (!response.ok && response.status !== 404) throw new Error("Could not delete the connected scan. Please retry.")
}

export async function scanBatch(
  items: { url: string; label?: string }[],
  persona: Persona
): Promise<BatchScanResponse> {
  const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "")
  const res = await fetch(`${base}/api/v1/analyze/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      persona_mode: persona,
      items,
      prefer_cache: true
    })
  })
  if (!res.ok) {
    throw new Error(`Batch scan failed (${res.status}). Please check links and retry.`)
  }
  const data = await res.json()
  return {
    batchId: data.batch_id,
    createdAt: data.created_at,
    totalItems: data.total_items,
    personaMode: data.persona_mode,
    aggregateTrustScore: data.aggregate_trust_score,
    highRiskCount: data.high_risk_count,
    moderateRiskCount: data.moderate_risk_count,
    lowRiskCount: data.low_risk_count,
    auditSignature: data.audit_signature,
    items: (data.items || []).map((it: any) => ({
      url: it.url,
      label: it.label,
      status: it.status,
      trustScore: it.trust_score,
      confidence: it.confidence,
      riskCategory: it.risk_category,
      matchedDomainsCount: it.matched_domains_count,
      topMatches: (it.top_matches || []).map((m: any) => ({
        domain: m.domain,
        url: m.link || "",
        title: m.title || "Match",
        price: m.extracted_price,
        currency: m.currency,
        whitelisted: m.is_whitelisted,
        flagged: m.flagged,
        sourceIcon: m.source_icon
      })),
      explanation: it.explanation,
      cacheHit: it.cache_hit,
      aiOverview: it.ai_overview,
      isSynthetic: it.is_synthetic === true,
      provenanceSummary: it.provenance_summary,
      detectedGenerators: Array.isArray(it.detected_generators) ? it.detected_generators : [],
      pricingAnalysis: it.pricing_analysis
    }))
  }
}

