"use client";

import { useEffect, useRef, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { PDF_FILE, publicUrl } from "@/lib/base-path";

type Status = "loading" | "ready" | "missing" | "error";

export function PdfViewer() {
  const url = publicUrl(`/${PDF_FILE}`);
  const frameRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<Status>("loading");
  const [pageCount, setPageCount] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    const frame = frameRef.current;
    let cancelled = false;

    async function load() {
      if (!container || !frame) return;
      container.replaceChildren();
      try {
        const response = await fetch(url);
        if (!response.ok) {
          if (!cancelled) setStatus("missing");
          return;
        }
        const bytes = new Uint8Array(await response.arrayBuffer());
        const header = String.fromCharCode(...bytes.slice(0, 5));
        if (!header.startsWith("%PDF")) {
          if (!cancelled) setStatus("error");
          return;
        }

        const pdfjs = await import("pdfjs-dist");
        pdfjs.GlobalWorkerOptions.workerSrc = publicUrl("/pdf.worker.min.mjs");
        const pdf = await pdfjs.getDocument({ data: bytes.slice(0) }).promise;
        if (cancelled) return;

        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
          if (cancelled) return;
          const page = await pdf.getPage(pageNumber);
          const unscaled = page.getViewport({ scale: 1 });
          const width = frame.clientWidth || unscaled.width;
          const viewport = page.getViewport({ scale: width / unscaled.width });
          const canvas = document.createElement("canvas");
          const ratio = Math.min(window.devicePixelRatio || 1, 2);
          canvas.width = Math.floor(viewport.width * ratio);
          canvas.height = Math.floor(viewport.height * ratio);
          canvas.style.width = "100%";
          canvas.style.height = "auto";
          canvas.className = "block bg-white";
          const context = canvas.getContext("2d");
          if (!context) continue;
          context.setTransform(ratio, 0, 0, ratio, 0, 0);

          const figure = document.createElement("figure");
          figure.className = "overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-foreground/10";
          const caption = document.createElement("figcaption");
          caption.className = "border-b px-3 py-2 text-xs text-neutral-600";
          caption.textContent = `Page ${pageNumber}`;
          figure.append(caption, canvas);
          container.append(figure);

          await page.render({ canvas, viewport }).promise;
        }

        if (!cancelled) {
          setPageCount(pdf.numPages);
          setStatus("ready");
        }
      } catch {
        container?.replaceChildren();
        if (!cancelled) setStatus("error");
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [url]);

  return (
    <div ref={frameRef} className="space-y-4">
      {status === "loading" ? (
        <div aria-busy="true" aria-live="polite" className="space-y-3">
          <p>Chargement de la synthèse…</p>
          <div className="h-80 animate-pulse rounded-lg bg-muted" />
        </div>
      ) : null}

      {status === "missing" ? (
        <Alert variant="destructive">
          <AlertTitle>Synthèse introuvable</AlertTitle>
          <AlertDescription>
            Le fichier {PDF_FILE} n’est pas accessible.
          </AlertDescription>
        </Alert>
      ) : null}

      {status === "error" ? (
        <div className="space-y-4">
          <Alert variant="destructive">
            <AlertTitle>Affichage impossible</AlertTitle>
            <AlertDescription>
              La synthèse n’a pas pu être affichée page par page. Le fichier reste
              proposé dans le cadre ci-dessous et en téléchargement.
            </AlertDescription>
          </Alert>
          <iframe
            src={url}
            title="Nutrition ASV, synthèse"
            className="h-[75vh] w-full rounded-lg bg-white ring-1 ring-foreground/10"
          />
        </div>
      ) : null}

      <div
        ref={containerRef}
        className={status === "ready" ? "space-y-4" : "hidden"}
        aria-label="Pages de la synthèse"
      />

      {status === "ready" ? (
        <p className="text-sm text-muted-foreground">
          {pageCount} {pageCount > 1 ? "pages affichées" : "page affichée"}.
        </p>
      ) : null}
    </div>
  );
}
