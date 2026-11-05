"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { coursePdfPath, courseQuizPath, getCourse } from "@/data/courses";

export function SiteHeader() {
  const pathname = usePathname();
  const courseId = pathname.match(/^\/cours\/([^/]+)/)?.[1];
  const course = courseId ? getCourse(courseId) : undefined;

  return (
    <header className="sticky top-0 z-20 border-b bg-background/95 backdrop-blur">
      <div className="h-1 bg-[oklch(0.58_0.14_42)]" />
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <div className="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-1">
          <Link href="/" className="font-heading text-xl leading-none tracking-tight">
            Synthèses
          </Link>
          {course ? (
            <span className="truncate text-sm text-muted-foreground">{course.title}</span>
          ) : null}
        </div>
        {course ? (
          <nav className="flex items-center gap-1" aria-label={course.title}>
            <Button asChild variant="ghost" className="h-11 px-3">
              <Link href={coursePdfPath(course.id)}>Synthèse</Link>
            </Button>
            <Button asChild variant="ghost" className="h-11 px-3">
              <Link href={courseQuizPath(course.id)}>Entraînement</Link>
            </Button>
          </nav>
        ) : null}
      </div>
    </header>
  );
}
