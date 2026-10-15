import Link from "next/link";
import { SectionList } from "@/components/section-list";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:py-16">
      <p className="text-sm font-medium tracking-wide text-[oklch(0.48_0.12_42)]">
        Document de révision
      </p>
      <h1 className="mt-2 font-heading text-4xl leading-tight sm:text-6xl">Nutrition ASV</h1>
      <p className="mt-3 font-heading text-xl text-muted-foreground sm:text-2xl">
        La synthèse pour comprendre et mémoriser
      </p>
      <p className="mt-6 max-w-2xl text-lg leading-relaxed">
        Lis la synthèse dans la page, puis réponds aux questions de chaque section.
        Après chaque réponse, l’extrait affiché est repris tel quel du document.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Lire la synthèse</CardTitle>
            <CardDescription>
              Le PDF s’affiche dans la page. Tu peux aussi le télécharger.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>Sept sections, dans l’ordre du document.</p>
          </CardContent>
          <CardFooter>
            <Button asChild className="h-11 px-4">
              <Link href="/lire">Ouvrir la synthèse</Link>
            </Button>
          </CardFooter>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>S’entraîner</CardTitle>
            <CardDescription>
              Questionnaires par section, score, extrait et nouvelle tentative.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>Le meilleur score reste enregistré sur cet appareil.</p>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" className="h-11 px-4">
              <Link href="/entrainement">Choisir une section</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>

      <section className="mt-12">
        <h2 className="font-heading text-2xl">Sections de la synthèse</h2>
        <div className="mt-4">
          <SectionList />
        </div>
      </section>
    </div>
  );
}
