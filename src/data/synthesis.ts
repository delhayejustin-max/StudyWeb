import bank from "./bank.json";
import type { StudySection } from "./types";

export const sections = bank.sections as StudySection[];

export function getSection(id: string): StudySection | undefined {
  return sections.find((section) => section.id === id);
}

export function getNextSection(id: string): StudySection | null {
  const index = sections.findIndex((section) => section.id === id);
  if (index < 0 || index + 1 >= sections.length) return null;
  return sections[index + 1] ?? null;
}
