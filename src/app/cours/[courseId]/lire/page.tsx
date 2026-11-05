import Link from "next/link";
import { notFound } from "next/navigation";
import { PdfViewer } from "@/components/pdf-viewer";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { courseQuizPath, courses, getCourse, questionCount } from "@/data/courses";
import { publicUrl } from "@/lib/base-path";

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
  return { title: course ? `Lire ${course.title}` : "Synthèse" };
}

export default async function LirePage({
  params,
}: {
  params: Promise<{ courseId: string }>;
}) {
  const { courseId } = await params;
  const course = getCourse(courseId);
  if (!course) notFound();

  const pdfUrl = course.pdf ? publicUrl(`/${course.pdf}`) : "";
  const questions = questionCount(course);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:py-10">
      <p className="text-sm text-muted-foreground">{course.label}</p>
      <h1 className="mt-2 font-heading text-3xl sm:text-4xl">{course.title}</h1>
      <div className="mt-5 flex flex-col gap-2 sm:flex-row">
        {course.pdf ? (
          <Button asChild className="h-11 px-4">
            <a href={pdfUrl} download={course.pdf}>
              Télécharger le PDF
            </a>
          </Button>
        ) : null}
        <Button asChild variant="outline" className="h-11 px-4">
          <Link href={courseQuizPath(course.id)}>
            {questions === 0 ? "Voir les questions" : "S’entraîner"}
          </Link>
        </Button>
      </div>
      <div className="mt-6">
        {course.pdf ? (
          <PdfViewer file={course.pdf} title={course.title} />
        ) : (
          <Alert>
            <AlertTitle>Pas de synthèse</AlertTitle>
            <AlertDescription>Ce cours n’a pas encore de PDF.</AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
}
