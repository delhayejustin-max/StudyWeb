"use client";

import Link from "next/link";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useBestScores } from "@/components/score-store";
import { courseSectionPath } from "@/data/courses";
import type { Course } from "@/data/types";
import { scoreKey } from "@/lib/scores";

export function SectionList({ course }: { course: Course }) {
  const { state } = useBestScores();

  if (course.sections.length === 0) {
    return (
      <Alert>
        <AlertTitle>Aucune question</AlertTitle>
        <AlertDescription>Aucune question pour ce cours.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-3">
      {state.status === "loading" ? (
        <p className="text-sm text-muted-foreground" aria-live="polite">
          Chargement des scores…
        </p>
      ) : null}
      {state.status === "error" ? (
        <Alert variant="destructive">
          <AlertTitle>Scores indisponibles</AlertTitle>
          <AlertDescription>
            Impossible de lire les scores enregistrés sur cet appareil.
          </AlertDescription>
        </Alert>
      ) : null}
      <ul className="space-y-3">
        {course.sections.map((section) => {
          const best =
            state.status === "ready"
              ? state.scores[scoreKey(course.id, section.id)]
              : undefined;
          const scoreLabel =
            state.status === "loading"
              ? "…"
              : state.status === "error"
                ? "Score non lu"
                : best
                  ? `Meilleur score ${best.correct}/${best.total}`
                  : "Aucun score";
          const countLabel =
            section.questions.length === 0
              ? "Aucune question"
              : `${section.questions.length} questions`;

          return (
            <li key={section.id}>
              <Link
                href={courseSectionPath(course.id, section.id)}
                className="flex min-h-16 flex-col gap-1 rounded-xl bg-card px-4 py-4 ring-1 ring-foreground/10 transition-colors hover:bg-muted sm:flex-row sm:items-center sm:justify-between"
              >
                <span className="font-heading text-lg leading-snug">{section.title}</span>
                <span className="text-sm text-muted-foreground">
                  {countLabel}
                  <span aria-hidden="true"> · </span>
                  {scoreLabel}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
