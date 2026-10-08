import { cn } from "@/lib/utils"

interface TrustScoreRingProps {
  /** 0-100, or null for insufficient data */
  score: number | null
  toneClass: string
  size?: number
  className?: string
}

export function TrustScoreRing({ score, toneClass, size = 132, className }: TrustScoreRingProps) {
  const stroke = 10
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const pct = score ?? 0
  const dash = (pct / 100) * circumference

  return (
    <div className={cn("inline-flex shrink-0 flex-col items-center justify-center", className)}>
      <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={stroke}
          className="text-muted"
          stroke="currentColor"
        />
        {score !== null && (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circumference}`}
            className={cn("transition-[stroke-dasharray] duration-700 ease-out", toneClass)}
            stroke="currentColor"
          />
        )}
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        {score === null ? (
          <span className="text-2xl font-semibold text-muted-foreground">—</span>
        ) : (
          <span className={cn("text-3xl font-semibold tabular-nums", toneClass)}>{score}</span>
        )}
      </div>
      </div>
      <span className="mt-1 whitespace-nowrap text-[10px] font-medium uppercase tracking-wide text-muted-foreground">{score === null ? "No score" : "Evidence score"}</span>
    </div>
  )
}
