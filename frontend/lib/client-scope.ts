const STORAGE_KEY = "verix_client_id"
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

/** Used only for connected requests; never include this value in UI or reports. */
export function clientScopeHeaders(): Headers {
  if (typeof window === "undefined") throw new Error("Connected scans require a browser session.")
  let id: string
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    if (stored && UUID.test(stored)) id = stored
    else {
      id = window.crypto.randomUUID()
      window.localStorage.setItem(STORAGE_KEY, id)
    }
  } catch {
    throw new Error("Allow local storage to keep connected scans associated with this browser, or use Demo mode.")
  }
  return new Headers({ "X-Client-Id": id })
}

/** Resolves the API base URL across local dev, remote, or unified container deployments. */
export function getApiBaseUrl(): string {
  let base = (process.env.NEXT_PUBLIC_API_BASE_URL || "").trim()
  if (!base && typeof window !== "undefined") {
    // When running under Next.js dev server (port 3000), target FastAPI on port 8000
    if (window.location.port === "3000") {
      base = `${window.location.protocol}//${window.location.hostname}:8000`
    } else {
      // In production unified deployment, the API is served from the same origin
      base = window.location.origin
    }
  }
  if (!base) {
    base = "http://127.0.0.1:8000"
  }
  return base.replace(/\/$/, "")
}

/** Central request boundary for the scoped FastAPI endpoints. */
export function scopedApiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  if (!/^\/api\/v1\/[a-zA-Z0-9_/.-]+(?:\?.*)?$/.test(path)) {
    throw new Error("Unsupported scoped API endpoint.")
  }
  const headers = new Headers(init.headers)
  clientScopeHeaders().forEach((value, key) => headers.set(key, value))
  
  const base = getApiBaseUrl()
  return fetch(`${base}${path}`, { ...init, headers, cache: "no-store", redirect: "error" })
}

