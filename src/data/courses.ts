import bank from "./bank.json";
import bio from "./bio.json";
import type { Course, StudySection } from "./types";

/**
 * Catalogue des cours.
 * Pour ajouter un cours : déposer son PDF dans `public/`, puis ajouter une entrée ici.
 * Les pages lisent ce tableau. Elles n'ont pas à être réécrites.
 * `pdf` est le nom du fichier dans `public/` (chaîne vide s'il n'y a pas encore de PDF).
 * `sections` porte les questions. Un tableau vide affiche l'état « aucune question ».
 */
export const courses: Course[] = [
  {
    id: "nutrition-asv",
    title: "Nutrition ASV",
    label: "La synthèse pour comprendre et mémoriser",
    pdf: "Nutrition_ASV_synthese.pdf",
    sections: bank.sections as StudySection[],
  },
  {
    id: "caracteristiques-du-vivant",
    title: "Les caractéristiques du vivant",
    label: "Les caractéristiques du vivant",
    pdf: "Les_caracteristiques_du_vivant.pdf",
    sections: bio.sections as StudySection[],
  },
];

export function getCourse(id: string): Course | undefined {
  return courses.find((course) => course.id === id);
}

export function questionCount(course: Course): number {
  return course.sections.reduce((sum, section) => sum + section.questions.length, 0);
}

export function coursePdfPath(courseId: string): string {
  return `/cours/${courseId}/lire`;
}

export function courseQuizPath(courseId: string): string {
  return `/cours/${courseId}/entrainement`;
}

export function courseSectionPath(courseId: string, sectionId: string): string {
  return `/cours/${courseId}/entrainement/${sectionId}`;
}
