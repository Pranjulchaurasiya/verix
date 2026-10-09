// Major trusted platforms. Matches from these domains skip the risk pipeline.
export const TRUSTED_DOMAINS: { domain: string; label: string }[] = [
  { domain: "amazon.in", label: "Amazon" },
  { domain: "amazon.com", label: "Amazon" },
  { domain: "flipkart.com", label: "Flipkart" },
  { domain: "meesho.com", label: "Meesho" },
  { domain: "myntra.com", label: "Myntra" },
  { domain: "ajio.com", label: "Ajio" },
  { domain: "nykaa.com", label: "Nykaa" },
  { domain: "tatacliq.com", label: "Tata CLiQ" },
]

const TRUSTED_SET = new Set(TRUSTED_DOMAINS.map((d) => d.domain))

export function isWhitelisted(domain: string): boolean {
  const bare = domain.replace(/^www\./, "").toLowerCase()
  return TRUSTED_SET.has(bare)
}
