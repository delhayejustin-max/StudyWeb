"use client";

import { useState } from "react";
import Link from "next/link";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useBestScores } from "@/components/score-store";
import type { Question, StudySection } from "@/data/types";
import { cn } from "@/lib/utils";

type Given = {
  correct: boolean;
  label: string;
};

type Phase = "question" | "results";

function isCorrect(question: Question, selection: string): boolean {
  if (question.type === "mc") return selection === question.correctChoiceId;
  return (selection === "true") === question.correct;
}

function givenLabel(question: Question, selection: string): string {
  if (question.type === "tf") return selection === "true" ? "Vrai" : "Faux";
  return question.choices.find((choice) => choice.id === selection)?.text ?? selection;
}

export function Quiz({
  section,
  nextSection,
}: {
  section: StudySection;
  nextSection: { id: string; title: string } | null;
}) {
  const questions = section.questions;
  const { state: scoreState, record } = useBestScores();
  const [phase, setPhase] = useState<Phase>("question");
  const [index, setIndex] = useState(0);
  const [selection, setSelection] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [answers, setAnswers] = useState<Record<string, Given>>({});
  const [improved, setImproved] = useState(false);

  const question = questions[index];
  const correctCount = questions.filter((item) => answers[item.id]?.correct).length;
  const answeredCount = Object.keys(answers).length;
  const progress = questions.length === 0 ? 0 : Math.round((answeredCount / questions.length) * 100);

  function retry() {
    setPhase("question");
    setIndex(0);
    setSelection(null);
    setRevealed(false);
    setAnswers({});
    setImproved(false);
  }

  if (questions.length === 0 || !question) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 px-4 py-8">
        <h1 className="font-heading text-3xl leading-tight">{section.title}</h1>
        <Alert>
          <AlertTitle>Aucune question</AlertTitle>
          <AlertDescription>Aucune question dans cette section.</AlertDescription>
        </Alert>
        <Button asChild variant="outline" className="h-11">
          <Link href="/entrainement">Toutes les sections</Link>
        </Button>
      </div>
    );
  }

  function validate() {
    if (!selection || revealed) return;
    setAnswers((current) => ({
      ...current,
      [question.id]: {
        correct: isCorrect(question, selection),
        label: givenLabel(question, selection),
      },
    }));
    setRevealed(true);
  }

  function goNext() {
    if (index + 1 >= questions.length) {
      const result = record(section.id, correctCount, questions.length);
      setImproved(result.ok && result.improved);
      setPhase("results");
      return;
    }
    setIndex((value) => value + 1);
    setSelection(null);
    setRevealed(false);
  }

  const best =
    scoreState.status === "ready" ? scoreState.scores[section.id] : undefined;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <p className="text-sm text-muted-foreground">
        <Link href="/entrainement" className="underline-offset-4 hover:underline">
          Entraînement
        </Link>
      </p>
      <h1 className="mt-2 font-heading text-3xl leading-tight sm:text-4xl">{section.title}</h1>
      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between gap-3 text-sm text-muted-foreground">
          <span>
            {phase === "results"
              ? "Tentative terminée"
              : `Question ${index + 1} sur ${questions.length}`}
          </span>
          <span>
            {scoreState.status === "loading"
              ? "Chargement des scores…"
              : scoreState.status === "error"
                ? "Scores indisponibles"
                : best
                  ? `Meilleur score ${best.correct}/${best.total}`
                  : "Aucun score"}
          </span>
        </div>
        <Progress value={phase === "results" ? 100 : progress} />
      </div>

      {phase === "question" ? (
        <Card className="mt-6">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{question.type === "mc" ? "QCM" : "Vrai ou faux"}</Badge>
            </div>
            <CardTitle className="text-xl leading-snug sm:text-2xl">{question.prompt}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {question.type === "tf" ? (
              <blockquote className="rounded-lg bg-muted px-4 py-3 font-heading text-lg leading-relaxed">
                {question.statement}
              </blockquote>
            ) : null}

            <div className="space-y-2" role="group" aria-label="Réponses">
              {question.type === "mc"
                ? question.choices.map((choice) => (
                    <ChoiceButton
                      key={choice.id}
                      pressed={selection === choice.id}
                      disabled={revealed}
                      tone={toneFor(revealed, selection === choice.id, choice.id === question.correctChoiceId)}
                      onClick={() => setSelection(choice.id)}
                    >
                      {choice.text}
                    </ChoiceButton>
                  ))
                : (["true", "false"] as const).map((value) => (
                    <ChoiceButton
                      key={value}
                      pressed={selection === value}
                      disabled={revealed}
                      tone={toneFor(
                        revealed,
                        selection === value,
                        (value === "true") === question.correct,
                      )}
                      onClick={() => setSelection(value)}
                    >
                      {value === "true" ? "Vrai" : "Faux"}
                    </ChoiceButton>
                  ))}
            </div>

            {revealed ? (
              <div aria-live="polite" className="space-y-3 pt-2">
                <p className={answers[question.id]?.correct ? "text-success" : "text-destructive"}>
                  {answers[question.id]?.correct ? "Bonne réponse." : "À revoir."}
                </p>
                <SourceBlock
                  source={question.source}
                  sourceSectionTitle={question.sourceSectionTitle}
                />
              </div>
            ) : null}

            <div className="flex flex-wrap gap-2 pt-2">
              {!revealed ? (
                <Button type="button" className="h-11 px-4" disabled={!selection} onClick={validate}>
                  Valider
                </Button>
              ) : (
                <Button type="button" className="h-11 px-4" onClick={goNext}>
                  {index + 1 >= questions.length ? "Voir le score" : "Question suivante"}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Results
          section={section}
          questions={questions}
          answers={answers}
          correctCount={correctCount}
          improved={improved}
          scoreState={scoreState.status}
          nextSection={nextSection}
          onRetry={retry}
        />
      )}
    </div>
  );
}

function toneFor(revealed: boolean, selected: boolean, correct: boolean) {
  if (!revealed) return selected ? "selected" : "idle";
  if (correct) return "right";
  if (selected) return "wrong";
  return "idle";
}

function ChoiceButton({
  children,
  pressed,
  disabled,
  tone,
  onClick,
}: {
  children: string;
  pressed: boolean;
  disabled: boolean;
  tone: "idle" | "selected" | "right" | "wrong";
  onClick: () => void;
}) {
  return (
    <Button
      type="button"
      variant="outline"
      aria-pressed={pressed}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "h-auto min-h-12 w-full justify-start px-4 py-3 text-left text-base whitespace-normal disabled:opacity-100",
        tone === "selected" && "border-primary bg-primary/10",
        tone === "right" && "border-success bg-success/10",
        tone === "wrong" && "border-destructive bg-destructive/10",
      )}
    >
      {children}
    </Button>
  );
}

function SourceBlock({
  source,
  sourceSectionTitle,
}: {
  source: string;
  sourceSectionTitle?: string;
}) {
  return (
    <figure className="space-y-2 rounded-lg border bg-background px-4 py-3">
      <figcaption className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
        Extrait de la synthèse
      </figcaption>
      <blockquote className="font-heading text-base leading-relaxed">{source}</blockquote>
      {sourceSectionTitle ? (
        <p className="text-sm text-muted-foreground">
          Cette phrase est écrite dans la section « {sourceSectionTitle} ».
        </p>
      ) : null}
    </figure>
  );
}

function Results({
  section,
  questions,
  answers,
  correctCount,
  improved,
  scoreState,
  nextSection,
  onRetry,
}: {
  section: StudySection;
  questions: Question[];
  answers: Record<string, Given>;
  correctCount: number;
  improved: boolean;
  scoreState: "loading" | "ready" | "error";
  nextSection: { id: string; title: string } | null;
  onRetry: () => void;
}) {
  const wrong = questions.filter((question) => !answers[question.id]?.correct);
  const percent = questions.length === 0 ? 0 : Math.round((correctCount / questions.length) * 100);

  return (
    <div className="mt-6 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-3xl">
            {correctCount} / {questions.length}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>Score de la tentative : {percent} %.</p>
          {improved ? <p>Nouveau meilleur score.</p> : null}
          {scoreState === "error" ? (
            <p>Le score de cette tentative n’a pas pu être enregistré sur cet appareil.</p>
          ) : null}
        </CardContent>
      </Card>

      {wrong.length === 0 ? (
        <Alert>
          <AlertTitle>Tentative juste</AlertTitle>
          <AlertDescription>Toutes les réponses correspondent aux extraits.</AlertDescription>
        </Alert>
      ) : (
        <div className="space-y-3">
          <h2 className="font-heading text-2xl">Réponses à revoir</h2>
          <ul className="space-y-3">
            {wrong.map((question) => (
              <li key={question.id}>
                <Card>
                  <CardHeader>
                    <CardTitle className="leading-snug">{question.prompt}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {question.type === "tf" ? (
                      <p className="font-heading leading-relaxed">{question.statement}</p>
                    ) : null}
                    <p className="text-sm">
                      Ta réponse : {answers[question.id]?.label ?? "—"}
                    </p>
                    <SourceBlock
                      source={question.source}
                      sourceSectionTitle={question.sourceSectionTitle}
                    />
                  </CardContent>
                </Card>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
        <Button type="button" className="h-11 px-4" onClick={onRetry}>
          Recommencer
        </Button>
        {nextSection ? (
          <Button asChild variant="outline" className="h-11 px-4">
            <Link href={`/entrainement/${nextSection.id}`}>{nextSection.title}</Link>
          </Button>
        ) : null}
        <Button asChild variant="ghost" className="h-11 px-4">
          <Link href="/entrainement">Toutes les sections</Link>
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">Section : {section.title}</p>
    </div>
  );
}
