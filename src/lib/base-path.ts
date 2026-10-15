/** Prefix for files in public/. Next.js Link already applies basePath. */
export function publicUrl(path: string): string {
  const raw = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
  const base = raw === "/" ? "" : raw.replace(/\/$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}

export const PDF_FILE = "Nutrition_ASV_synthese.pdf";
