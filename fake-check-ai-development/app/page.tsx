import { SiteHeader } from "@/components/site-header"
import { CheckExperience } from "@/components/check-experience"

export default function HomePage() {
  return (
    <div className="min-h-svh bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-12">
        <CheckExperience />
      </main>
    </div>
  )
}
