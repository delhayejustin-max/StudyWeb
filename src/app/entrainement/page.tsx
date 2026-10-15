import { SectionList } from "@/components/section-list";

export const metadata = {
  title: "Entraînement",
};

export default function EntrainementPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:py-10">
      <h1 className="font-heading text-3xl sm:text-4xl">Entraînement</h1>
      <p className="mt-3 max-w-2xl leading-relaxed text-muted-foreground">
        Chaque section porte le titre du document. Réponds, lis l’extrait, puis
        recommence si tu veux améliorer le score.
      </p>
      <div className="mt-6">
        <SectionList />
      </div>
    </div>
  );
}
