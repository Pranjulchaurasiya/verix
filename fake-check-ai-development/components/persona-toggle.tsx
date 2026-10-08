"use client"

import { ShoppingBag, Camera } from "lucide-react"
import type { Persona } from "@/lib/types"
import { cn } from "@/lib/utils"

const OPTIONS: {
  value: Persona
  title: string
  desc: string
  icon: typeof ShoppingBag
}[] = [
  {
    value: "buyer",
    title: "Buyer check",
    desc: "See where else this photo is used",
    icon: ShoppingBag,
  },
  {
    value: "seller",
    title: "Creator protection",
    desc: "Review potential photo reuse",
    icon: Camera,
  },
]

export function PersonaToggle({
  value,
  onChange,
}: {
  value: Persona
  onChange: (p: Persona) => void
}) {
  return (
    <div className="persona-switch" role="group" aria-label="What do you want to do?">
      {OPTIONS.map((opt) => {
        const active = value === opt.value
        const Icon = opt.icon
        return (
          <button
            key={opt.value}
            type="button"
            aria-pressed={active}
            onClick={() => onChange(opt.value)}
            className={cn(
              "persona-option", active && "is-active",
            )}
          >
            <span
              className={cn(
                "flex shrink-0 items-center justify-center",
              )}
            >
              <Icon className="size-4" />
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-medium leading-tight">{opt.title}</span>
            </span>
          </button>
        )
      })}
    </div>
  )
}
