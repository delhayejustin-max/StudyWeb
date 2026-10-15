import { notFound } from "next/navigation";
import { Quiz } from "@/components/quiz";
import { getNextSection, getSection, sections } from "@/data/synthesis";

export function generateStaticParams() {
  return sections.map((section) => ({ sectionId: section.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ sectionId: string }>;
}) {
  const { sectionId } = await params;
  const section = getSection(sectionId);
  return { title: section?.title ?? "Section" };
}

export default async function SectionPage({
  params,
}: {
  params: Promise<{ sectionId: string }>;
}) {
  const { sectionId } = await params;
  const section = getSection(sectionId);
  if (!section) notFound();
  const next = getNextSection(sectionId);

  return (
    <Quiz
      section={section}
      nextSection={next ? { id: next.id, title: next.title } : null}
    />
  );
}
