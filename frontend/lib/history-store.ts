"use client"

import { useCallback, useSyncExternalStore } from "react"
import type { CheckResult } from "./types"

/**
 * Local history retains investigations completed on this device (both live API scans
 * and simulated demo cases) so results are instantly retrievable offline.
 */

const KEY = "fakecheck.history.v1"
const MAX = 50
const EMPTY: CheckResult[] = []

function read(): CheckResult[] {
  if (typeof window === "undefined") return []
  try {
    const raw = window.localStorage.getItem(KEY)
    const parsed: unknown = raw ? JSON.parse(raw) : []
    const validItems = Array.isArray(parsed) ? parsed.filter(item => item && typeof item.id === "string" && Array.isArray(item.matches) && Array.isArray(item.signals)) : []
    return validItems
  } catch {
    return []
  }
}

let cache: CheckResult[] = read()
const listeners = new Set<() => void>()

function emit() {
  for (const l of listeners) l()
}

function persist(next: CheckResult[]) {
  cache = next
  try {
    window.localStorage.setItem(KEY, JSON.stringify(next))
  } catch {
    emit()
    throw new Error("History could not be saved on this device")
  }
  emit()
}

export function addCheck(result: CheckResult) {
  if (!result || typeof result.id !== "string") return
  persist([result, ...cache.filter((c) => c.id !== result.id)].slice(0, MAX))
}

export function removeCheck(id: string) {
  persist(cache.filter((c) => c.id !== id))
}

export function clearHistory() {
  persist([])
}

function subscribe(cb: () => void) {
  listeners.add(cb)
  const onStorage = (e: StorageEvent) => {
    if (e.key === KEY) {
      cache = read()
      cb()
    }
  }
  window.addEventListener("storage", onStorage)
  return () => {
    listeners.delete(cb)
    window.removeEventListener("storage", onStorage)
  }
}

export function useHistory(): CheckResult[] {
  return useSyncExternalStore(
    subscribe,
    useCallback(() => cache, []),
    () => EMPTY,
  )
}
