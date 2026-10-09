export type Persona = "buyer" | "seller"

export type InputType = "url" | "upload" | "batch"

// The four visual states the UI must clearly distinguish.
export type Verdict = "trusted" | "low_risk" | "moderate_risk" | "insufficient_data" | "high_risk"

export type Confidence = "low" | "medium" | "high"
export type ProductAvailability = "in_stock" | "out_of_stock" | "discontinued" | "unknown"
export type ScanProvenance = "live_serpapi" | "cached" | "development_fallback" | "unknown"

export interface ImageMatch {
  /** Bare domain, e.g. "flipkart.com" */
  domain: string
  /** Full listing URL where the image was found */
  url: string
  /** Listing / page title reported by the reverse image search */
  title: string
  /** Numeric price in the given currency, when the source exposed one */
  price?: number
  currency?: string
  /** True when the domain is a pre-approved trusted marketplace */
  whitelisted: boolean
  /** True when this specific source contributed a risk signal */
  flagged: boolean
  /** Search engine that returned this source, when supplied by the API. */
  engine?: string
  /** Evidence class, such as visual_match, exact_match, product, or shopping. */
  evidenceType?: string
  /** Engines that independently returned this same canonical listing. */
  engines?: string[]
  evidenceTypes?: string[]
  corroborationCount?: number
  /** Time Verix retrieved this search result; not the listing publish date. */
  observedAt?: string
  legitimacyLabel?: string
  legitimacyScore?: number
  legitimacyReasons?: string[]
  sourceIcon?: string
  thumbnail?: string
}

export interface CheckResult {
  demo?: boolean
  whitelistBypass?: boolean
  recommendation?: string
  productAvailability?: ProductAvailability
  provenance?: ScanProvenance
  aiOverview?: string
  id: string
  createdAt: string
  persona: Persona
  inputType: InputType
  /** The image the user submitted (data URL for uploads, or the pasted URL) */
  imageUrl: string
  /** Original listing URL, when the user pasted a link */
  sourceUrl?: string
  verdict: Verdict
  /** Web-evidence score, not proof that a physical item is genuine. */
  trustScore: number | null
  confidence: Confidence
  /** Plain-language, non-accusatory summary */
  explanation: string
  /** Short, weighable risk signals (never hard accusations) */
  signals: string[]
  matches: ImageMatch[]
  /** Simulated-only example statistic; not shown as a live product benchmark. */
  medianPrice?: number
  currency?: string
  /** True when returned from cache because the live pipeline was degraded */
  degraded: boolean
  /** ISO timestamp of the underlying verified data (for fail-closed notes) */
  lastVerifiedAt: string
  isSynthetic?: boolean
  synthidDetected?: boolean
  provenanceSummary?: string
  detectedGenerators?: string[]
  pricingAnalysis?: any
  provenanceDetails?: any
}

export interface HealthEvent {
  at: string
  kind: "ok" | "degraded" | "recovered"
  message: string
}

export interface HealthStatus {
  /** Whether the upstream reverse-image-search (SerpApi) is answering */
  serpapiOk: boolean
  mode: "live" | "fail_closed"
  lastCheckAt: string
  latencyMs: number
  checksToday: number
  successRatePct: number
  recentEvents: HealthEvent[]
}

export interface BatchItemResult {
  url: string
  label?: string
  status: string
  trustScore?: number | null
  confidence?: Confidence
  riskCategory: Verdict
  matchedDomainsCount: number
  topMatches: ImageMatch[]
  explanation: string
  cacheHit: boolean
  aiOverview?: string
  isSynthetic?: boolean
  provenanceSummary?: string
  detectedGenerators?: string[]
  pricingAnalysis?: any
}

export interface BatchScanResponse {
  batchId: string
  createdAt: string
  totalItems: number
  personaMode: Persona
  aggregateTrustScore?: number | null
  highRiskCount: number
  moderateRiskCount: number
  lowRiskCount: number
  items: BatchItemResult[]
  auditSignature: string
}

