import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { coursePdfPath, courseQuizPath, courses, questionCount } from "@/data/courses";

export default function HomePage() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:py-16">
      <p className="text-sm font-medium tracking-wide text-[oklch(0.48_0.12_42)]">Cours</p>
      <h1 className="mt-2 font-heading text-4xl leading-tight sm:text-6xl">Synthèses</h1>
      <p className="mt-6 max-w-2xl text-lg leading-relaxed">
        Chaque cours a son PDF et son questionnaire. Après une réponse, l’extrait
        affiché est repris tel quel de la synthèse de ce cours.
      </p>

      {courses.length === 0 ? (
        <p className="mt-10 text-muted-foreground">Aucun cours pour le moment.</p>
      ) : (
        <ul className="mt-8 grid list-none gap-4 sm:grid-cols-2">
          {courses.map((course) => {
            const questions = questionCount(course);
            const sectionLabel =
              course.sections.length === 0
                ? "Aucune section"
                : course.sections.length === 1
                  ? "1 section"
                  : `${course.sections.length} sections`;
            const questionLabel =
              questions === 0
                ? "Aucune question"
                : questions === 1
                  ? "1 question"
                  : `${questions} questions`;

            return (
              <li key={course.id}>
                <Card className="h-full">
                  <CardHeader>
                    <p className="text-sm font-medium text-[oklch(0.48_0.12_42)]">{course.label}</p>
                    <CardTitle className="font-heading text-2xl">{course.title}</CardTitle>
                    <CardDescription>
                      {sectionLabel}
                      <span aria-hidden="true"> · </span>
                      {questionLabel}
                      {course.pdf ? "" : " · Pas de PDF"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p>
                      {course.pdf
                        ? "Lis la synthèse, puis réponds aux questions de ses sections."
                        : "La synthèse de ce cours n’est pas encore déposée."}
                    </p>
                  </CardContent>
                  <CardFooter className="flex flex-col gap-2 sm:flex-row">
                    <Button asChild className="h-11 w-full px-4 sm:w-auto">
                      <Link href={coursePdfPath(course.id)}>Lire la synthèse</Link>
                    </Button>
                    <Button asChild variant="outline" className="h-11 w-full px-4 sm:w-auto">
                      <Link href={courseQuizPath(course.id)}>S’entraîner</Link>
                    </Button>
                  </CardFooter>
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
