import type { CheckResult, Confidence, ImageMatch, InputType, Persona, Verdict } from "./types"
import { isWhitelisted } from "./whitelist"

/**
 * Mock analysis engine.
 *
 * In production this module is where the real pipeline lives:
 *   1. Call SerpApi's Google Lens engine with the submitted image.
 *   2. Normalize the visual matches (domain, url, title, price).
 *   3. Drop / short-circuit whitelisted trusted domains.
 *   4. Ask an LLM to turn the match set into a structured, non-accusatory verdict.
 *
 * Everything below deterministically simulates that so the frontend is fully
 * demoable without external keys. Swap `analyzeImage` for the real calls and the
 * UI keeps working unchanged.
 */

function hashSeed(seed: string): number {
  let h = 2166136261
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h)
}

function pickScenario(seed: string): Verdict {
  const s = seed.toLowerCase()
  if (s.includes("insufficient")) return "insufficient_data"
  if (s.includes("sneaker")) return "high_risk"
  if (s.includes("handbag")) return "trusted"
  const bucket = hashSeed(seed) % 100
  if (bucket < 38) return "high_risk"
  if (bucket < 68) return "low_risk"
  if (bucket < 86) return "trusted"
  return "insufficient_data"
}

const SKETCHY_DOMAINS = [
  "trend-bazaar-deals.shop",
  "mega-sale-outlet.store",
  "luxe-factory-direct.co",
  "clearance-hub99.online",
  "brandedfashion-sale.xyz",
  "topdeal-mart.site",
]

const NEUTRAL_DOMAINS = ["fashionista-blog.in", "styleforum.net", "productreview.com.au"]

function median(nums: number[]): number {
  if (nums.length === 0) return 0
  const sorted = [...nums].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[mid] : Math.round((sorted[mid - 1] + sorted[mid]) / 2)
}

function buildMatches(verdict: Verdict, seed: string): ImageMatch[] {
  if (seed === "example-sneaker") return [
    { domain: "brand-reference.example", url: "https://brand-reference.example/sneaker", title: "Reference catalog — demo sneaker", price: 12000, currency: "INR", whitelisted: true, flagged: false },
    { domain: "marketplace.example", url: "https://marketplace.example/sneaker", title: "Marketplace listing — demo sneaker", price: 11500, currency: "INR", whitelisted: true, flagged: false },
    ...[1900, 2200, 2500].map((price, i) => ({ domain: `merchant-${i + 1}.example`, url: `https://merchant-${i + 1}.example/sneaker`, title: "Matching photo — review suggested", price, currency: "INR", whitelisted: false, flagged: true })),
  ]
  const rnd = hashSeed(seed)
  const basePrice = 2400 + (rnd % 1800) // plausible INR listing price

  const trustedMatch = (domain: string, price: number): ImageMatch => ({
    domain,
    url: `https://www.${domain}/product/${(rnd % 999999).toString(36)}`,
    title: "Product listing",
    price,
    currency: "INR",
    whitelisted: true,
    flagged: false,
  })

  const sketchyMatch = (domain: string, price: number): ImageMatch => ({
    domain,
    url: `https://${domain}/p/${(rnd % 999999).toString(36)}`,
    title: "Limited stock — flash sale",
    price,
    currency: "INR",
    whitelisted: false,
    flagged: true,
  })

  switch (verdict) {
    case "trusted":
      return [
        trustedMatch("myntra.com", basePrice),
        trustedMatch("tatacliq.com", basePrice + 150),
        trustedMatch("ajio.com", basePrice - 100),
        {
          domain: NEUTRAL_DOMAINS[0],
          url: `https://${NEUTRAL_DOMAINS[0]}/review`,
          title: "Editor review",
          whitelisted: false,
          flagged: false,
        },
      ]
    case "moderate_risk":
    case "low_risk":
      return [
        trustedMatch("flipkart.com", basePrice),
        {
          domain: NEUTRAL_DOMAINS[1],
          url: `https://${NEUTRAL_DOMAINS[1]}/thread`,
          title: "Community discussion",
          whitelisted: false,
          flagged: false,
        },
        sketchyMatch(SKETCHY_DOMAINS[0], Math.round(basePrice * 0.82)),
      ]
    case "high_risk": {
      const low = Math.round(basePrice * 0.32)
      return [
        sketchyMatch(SKETCHY_DOMAINS[0], low),
        sketchyMatch(SKETCHY_DOMAINS[1], Math.round(basePrice * 0.29)),
        sketchyMatch(SKETCHY_DOMAINS[2], Math.round(basePrice * 0.35)),
        sketchyMatch(SKETCHY_DOMAINS[3], Math.round(basePrice * 0.3)),
        sketchyMatch(SKETCHY_DOMAINS[4], Math.round(basePrice * 0.41)),
        {
          domain: NEUTRAL_DOMAINS[2],
          url: `https://${NEUTRAL_DOMAINS[2]}/listing`,
          title: "Marketplace mirror",
          whitelisted: false,
          flagged: true,
        },
      ]
    }
    case "insufficient_data":
      return [
        {
          domain: NEUTRAL_DOMAINS[0],
          url: `https://${NEUTRAL_DOMAINS[0]}/page`,
          title: "Single low-confidence match",
          whitelisted: false,
          flagged: false,
        },
      ]
  }
}

function scoreFor(verdict: Verdict, seed: string): number | null {
  const jitter = hashSeed(seed) % 8
  switch (verdict) {
    case "trusted":
      return 90 + (jitter % 8)
    case "moderate_risk":
    case "low_risk":
      return 70 + (jitter % 14)
    case "high_risk":
      return 16 + (jitter % 22)
    case "insufficient_data":
      return null
  }
}

function confidenceFor(verdict: Verdict, matchCount: number): Confidence {
  if (verdict === "insufficient_data") return "low"
  if (matchCount >= 5) return "high"
  if (matchCount >= 3) return "medium"
  return "low"
}

function explanationFor(verdict: Verdict, persona: Persona): string {
  const buyer = persona === "buyer"
  switch (verdict) {
    case "trusted":
      return buyer
        ? "This photo mainly appears on established marketplaces we already trust, with consistent pricing. That's a reassuring sign, though you should still confirm the seller and return policy before paying."
        : "Your photo is showing up on trusted, verified marketplaces. This is expected if you sell there — nothing here points to unauthorized reuse."
    case "moderate_risk":
    case "low_risk":
      return buyer
        ? "This photo appears on a small, consistent set of sources and pricing looks normal. Nothing stands out as a strong risk signal, but treat this as one input, not a guarantee."
        : "Your photo appears on a limited number of sources with normal pricing. No strong reuse signal right now — worth a periodic re-check."
    case "high_risk":
      return buyer
        ? "This photo appears across several unverified merchant domains at unusually low prices. Review the evidence and seller policies before purchasing; image matches alone do not establish authenticity."
        : "This exact photo appears on several unverified merchant domains you may not have authorized, some using unusually low prices. These are signals of possible unauthorized reuse for you to review — not a definitive finding."
    case "insufficient_data":
      return "We couldn't find enough matches of this image to form a reliable signal. This isn't a pass or a fail — there simply isn't enough data to weigh in yet."
  }
}

function signalsFor(verdict: Verdict, matches: ImageMatch[], medianPrice: number): string[] {
  const flaggedCount = matches.filter((m) => m.flagged).length
  const hasTrusted = matches.some((m) => m.whitelisted)
  switch (verdict) {
    case "trusted":
      return [
        "Primary source is a verified major marketplace",
        "Trusted-platform match — deep risk analysis skipped",
        "Pricing consistent across sources",
      ]
    case "moderate_risk":
    case "low_risk":
      return [
        `Photo found on ${matches.length} source${matches.length === 1 ? "" : "s"} with no clustering of unknown shops`,
        "Pricing within the normal observed range",
        hasTrusted ? "At least one trusted marketplace carries this product" : "No high-risk domain patterns detected",
      ]
    case "high_risk":
      return [
        `Photo appears on ${flaggedCount} unverified merchant domain${flaggedCount === 1 ? "" : "s"}`,
        `Extreme price disparity — some listings well below the median of ₹${medianPrice.toLocaleString("en-IN")}`,
        "Flagged listings require independent review; domain age has not been verified",
        hasTrusted ? "Trusted reference listings available for comparison" : "No trusted reference listing available",
      ]
    case "insufficient_data":
      return ["Too few matches found to form a reliable signal", "No trusted-marketplace match to anchor pricing"]
  }
}

export interface AnalyzeInput {
  persona: Persona
  inputType: InputType
  imageUrl: string
  sourceUrl?: string
  /** Stable seed so the same image yields the same result (filename+size, or the URL) */
  seed: string
}

export function analyzeImage(input: AnalyzeInput): CheckResult {
  const verdict = pickScenario(input.seed)
  const matches = buildMatches(verdict, input.seed)
  const priced = matches.filter((m) => typeof m.price === "number").map((m) => m.price as number)
  const medianPrice = median(priced)
  const now = new Date().toISOString()

  return {
    demo: true,
    id: `chk_${hashSeed(input.seed + now).toString(36)}`,
    createdAt: now,
    persona: input.persona,
    inputType: input.inputType,
    imageUrl: input.imageUrl,
    sourceUrl: input.sourceUrl,
    verdict,
    trustScore: scoreFor(verdict, input.seed),
    confidence: confidenceFor(verdict, matches.length),
    explanation: explanationFor(verdict, input.persona),
    signals: signalsFor(verdict, matches, medianPrice),
    matches,
    medianPrice: medianPrice || undefined,
    currency: "INR",
    degraded: input.seed.includes("cached"),
    lastVerifiedAt: input.seed.includes("cached") ? new Date(Date.now() - 86400000).toISOString() : now,
    domainReputation: {
      domain: input.sourceUrl ? (() => { try { return new URL(input.sourceUrl).hostname.replace(/^www\./, "") } catch { return "resell-kicks-india.in" } })() : "resell-kicks-india.in",
      status: verdict === "high_risk" ? "suspicious" : "trusted",
      trust_score: verdict === "high_risk" ? 38 : 95,
      verdict_label: verdict === "high_risk" ? "Consumer Complaints Detected on Forums & Watchdogs" : "Verified Store Domain with Clean Web Footprint",
      warning_signals: verdict === "high_risk" ? ["Multiple chargeback complaints reported", "Unverified merchant registration"] : [],
      snippet_samples: [
        verdict === "high_risk"
          ? "Shoppers on consumer forums report non-delivery and unboxed replica goods from this storefront."
          : "Verified brand distributor with standard return and dispute resolution policies."
      ],
      sources_analyzed: 4
    },
    comparisonVideos: [
      {
        title: "Real vs Fake Comparison: How to Spot the Counterfeit",
        link: "https://www.youtube.com/results?search_query=real+vs+fake+unboxing",
        thumbnail: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        channel: "Authentic Sneaker Lab",
        views: "184K views",
        length: "8:24",
        published_date: "2 weeks ago"
      },
      {
        title: "Packaging & Serial Tag Forensic Unboxing Guide",
        link: "https://www.youtube.com/results?search_query=spot+counterfeit+packaging",
        thumbnail: "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400",
        channel: "Legit Check Live",
        views: "92K views",
        length: "5:12",
        published_date: "1 month ago"
      }
    ],
    retailerPriceMatrix: {
      query: "Authentic Product Benchmark",
      has_data: true,
      typical_price_range: "₹1,299 – ₹1,999",
      retailers: [
        {
          store_name: "Amazon India",
          domain: "amazon.in",
          price: "₹1,499",
          extracted_price: 1499,
          link: "https://www.amazon.in",
          rating: 4.4,
          reviews: 1420,
          delivery: "Prime Free Delivery",
          is_authorized: true,
          badge: "Authorized Seller"
        },
        {
          store_name: "Flipkart",
          domain: "flipkart.com",
          price: "₹1,399",
          extracted_price: 1399,
          link: "https://www.flipkart.com",
          rating: 4.3,
          reviews: 980,
          delivery: "Free Delivery",
          is_authorized: true,
          badge: "Assured Distributor"
        },
        {
          store_name: "Croma Electronics",
          domain: "croma.com",
          price: "₹1,599",
          extracted_price: 1599,
          link: "https://www.croma.com",
          rating: 4.5,
          reviews: 310,
          delivery: "Store Pickup Avail.",
          is_authorized: true,
          badge: "Official Retailer"
        }
      ]
    },
  }
}

export { isWhitelisted }
