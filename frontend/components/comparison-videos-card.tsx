"use client"

import { Video, ExternalLink, Play } from "lucide-react"

interface ComparisonVideosCardProps {
  comparisonVideos?: Array<{
    title?: string
    link?: string
    thumbnail?: string
    channel?: string
    views?: string
    length?: string
    published_date?: string
  }>
}

export function ComparisonVideosCard({ comparisonVideos }: ComparisonVideosCardProps) {
  if (!comparisonVideos || comparisonVideos.length === 0) return null

  return (
    <div className="rounded-xl border border-border bg-card p-4 transition-all">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/50 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded bg-red-600/10 p-1 text-red-600 dark:text-red-400">
            <Video className="size-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              Real vs. Fake Video Comparisons & Unboxing
            </h3>
            <p className="text-[11px] text-muted-foreground">
              Automated YouTube teardown intelligence for visual hardware comparison.
            </p>
          </div>
        </div>
        <span className="rounded bg-muted px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
          SerpApi YouTube
        </span>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 md:grid-cols-3">
        {comparisonVideos.map((video, idx) => (
          <a
            key={idx}
            href={video.link || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className="group relative flex flex-col overflow-hidden rounded-lg border border-border bg-background/60 transition-all hover:border-primary/50 hover:shadow-sm"
          >
            {video.thumbnail ? (
              <div className="relative aspect-video w-full overflow-hidden bg-muted">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={video.thumbnail}
                  alt={video.title || "Video thumbnail"}
                  className="size-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100">
                  <div className="flex size-8 items-center justify-center rounded-full bg-red-600 text-white shadow-md">
                    <Play className="size-4 fill-white ml-0.5" />
                  </div>
                </div>
                {video.length && (
                  <span className="absolute bottom-1 right-1 rounded bg-black/80 px-1 py-0.5 text-[10px] font-mono font-medium text-white">
                    {video.length}
                  </span>
                )}
              </div>
            ) : (
              <div className="flex aspect-video w-full items-center justify-center bg-muted/60 text-muted-foreground">
                <Video className="size-6" />
              </div>
            )}

            <div className="flex flex-1 flex-col justify-between p-2.5">
              <h4 className="line-clamp-2 text-xs font-medium text-foreground group-hover:text-primary transition-colors">
                {video.title}
              </h4>
              <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                <span className="truncate max-w-[120px] font-medium">{video.channel}</span>
                <span className="inline-flex items-center gap-0.5 text-primary">
                  Watch <ExternalLink className="size-2.5" />
                </span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
