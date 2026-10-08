import type { Verdict } from "@/lib/types"
import { VERDICT_META, toneClasses } from "@/lib/verdict-meta"
import { cn } from "@/lib/utils"

export function VerdictBadge({ verdict, className }: { verdict: Verdict; className?: string }) {
  const meta = VERDICT_META[verdict]
  const tone = toneClasses(meta.tone)
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium",
        tone.bg,
        tone.border,
        tone.text,
        className,
      )}
    >
      <span className={cn("size-1.5 rounded-full bg-current")} aria-hidden />
      {meta.label}
    </span>
  )
}
