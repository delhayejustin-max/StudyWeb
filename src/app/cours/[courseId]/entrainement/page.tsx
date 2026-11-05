import Link from "next/link";
import { notFound } from "next/navigation";
import { SectionList } from "@/components/section-list";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { coursePdfPath, courses, getCourse, questionCount } from "@/data/courses";

export function generateStaticParams() {
  return courses.map((course) => ({ courseId: course.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ courseId: string }>;
}) {
  const { courseId } = await params;
  const course = getCourse(courseId);
  return { title: course ? `Entraînement ${course.title}` : "Entraînement" };
}

export default async function EntrainementPage({
  params,
}: {
  params: Promise<{ courseId: string }>;
}) {
  const { courseId } = await params;
  const course = getCourse(courseId);
  if (!course) notFound();
  const questions = questionCount(course);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:py-10">
      <p className="text-sm text-muted-foreground">{course.label}</p>
      <h1 className="mt-2 font-heading text-3xl sm:text-4xl">Entraînement</h1>
      <p className="mt-1 font-heading text-lg text-muted-foreground">{course.title}</p>
      <p className="mt-3 max-w-2xl leading-relaxed text-muted-foreground">
        Chaque section porte le titre du document. Réponds, lis l’extrait, puis
        recommence si tu veux améliorer le score.
      </p>
      <div className="mt-4">
        <Button asChild variant="outline" className="h-11 px-4">
          <Link href={coursePdfPath(course.id)}>Lire la synthèse</Link>
        </Button>
      </div>
      <div className="mt-6">
        {questions === 0 ? (
          <Alert>
            <AlertTitle>Aucune question</AlertTitle>
            <AlertDescription>Aucune question pour ce cours.</AlertDescription>
          </Alert>
        ) : (
          <SectionList course={course} />
        )}
      </div>
    </div>
  );
}
