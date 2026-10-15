import Link from "next/link";
import { PdfViewer } from "@/components/pdf-viewer";
import { Button } from "@/components/ui/button";
import { PDF_FILE, publicUrl } from "@/lib/base-path";

export const metadata = {
  title: "Lire la synthèse",
};

export default function LirePage() {
  const pdfUrl = publicUrl(`/${PDF_FILE}`);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:py-10">
      <h1 className="font-heading text-3xl sm:text-4xl">Nutrition ASV</h1>
      <p className="mt-2 font-heading text-lg text-muted-foreground">
        La synthèse pour comprendre et mémoriser
      </p>
      <div className="mt-5 flex flex-col gap-2 sm:flex-row">
        <Button asChild className="h-11 px-4">
          <a href={pdfUrl} download={PDF_FILE}>
            Télécharger le PDF
          </a>
        </Button>
        <Button asChild variant="outline" className="h-11 px-4">
          <Link href="/entrainement">S’entraîner</Link>
        </Button>
      </div>
      <div className="mt-6">
        <PdfViewer />
      </div>
    </div>
  );
}
