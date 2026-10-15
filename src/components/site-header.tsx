import Link from "next/link";
import { Button } from "@/components/ui/button";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b bg-background/95 backdrop-blur">
      <div className="h-1 bg-[oklch(0.58_0.14_42)]" />
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <Link href="/" className="font-heading text-xl leading-none tracking-tight">
          Nutrition ASV
        </Link>
        <nav className="flex items-center gap-1" aria-label="Navigation">
          <Button asChild variant="ghost" className="h-11 px-3">
            <Link href="/lire">Synthèse</Link>
          </Button>
          <Button asChild variant="ghost" className="h-11 px-3">
            <Link href="/entrainement">Entraînement</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
