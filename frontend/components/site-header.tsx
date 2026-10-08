"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Activity } from "lucide-react"
import { cn } from "@/lib/utils"

const NAV = [
  { href: "/", label: "Check" },
  { href: "/history", label: "History" },
  { href: "/integrations", label: "Integrations" },
  { href: "/system", label: "System status" },
]

export function SiteHeader() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto flex min-h-16 w-full max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <img src="/verix-mark.svg" alt="" className="size-9" />
          <span className="text-2xl font-semibold tracking-[-0.06em]">
            verix<span className="ml-4 hidden border-l border-border pl-4 font-mono text-xs font-normal tracking-normal text-muted-foreground lg:inline">Image intelligence</span>
          </span>
        </Link>

        <div className="flex min-w-0 items-center gap-2">
        <nav aria-label="Main navigation" className="flex flex-wrap items-center gap-0.5">
          {NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "border-b-2 px-2 py-2 text-sm font-medium transition-colors sm:px-3",
                  active
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>
        <span className="hidden h-5 w-px bg-border sm:block" />
        <span className="hidden items-center gap-1.5 text-xs text-muted-foreground md:flex"><Activity className="size-3.5 text-primary" /> Image evidence</span>
        </div>
      </div>
    </header>
  )
}
