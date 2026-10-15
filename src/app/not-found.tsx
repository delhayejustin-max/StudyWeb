import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-16">
      <h1 className="font-heading text-3xl">Page introuvable</h1>
      <p className="mt-3 text-muted-foreground">Cette page n’existe pas.</p>
      <Button asChild className="mt-6 h-11 px-4">
        <Link href="/">Retour à l’accueil</Link>
      </Button>
    </div>
  );
}
