import { notFound } from "next/navigation";
import { Quiz } from "@/components/quiz";
import { courses, getCourse } from "@/data/courses";

export function generateStaticParams() {
  return courses.flatMap((course) =>
    course.sections.map((section) => ({
      courseId: course.id,
      sectionId: section.id,
    })),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ courseId: string; sectionId: string }>;
}) {
  const { courseId, sectionId } = await params;
  const course = getCourse(courseId);
  const section = course?.sections.find((item) => item.id === sectionId);
  return { title: section?.title ?? "Section" };
}

export default async function SectionPage({
  params,
}: {
  params: Promise<{ courseId: string; sectionId: string }>;
}) {
  const { courseId, sectionId } = await params;
  const course = getCourse(courseId);
  if (!course) notFound();
  const index = course.sections.findIndex((section) => section.id === sectionId);
  const section = index >= 0 ? course.sections[index] : undefined;
  if (!section) notFound();
  const next = course.sections[index + 1];

  return (
    <Quiz
      courseId={course.id}
      section={section}
      nextSection={next ? { id: next.id, title: next.title } : null}
    />
  );
}
