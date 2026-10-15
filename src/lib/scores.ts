export type BestScore = {
  correct: number;
  total: number;
  at: string;
};

const STORAGE_KEY = "nutrition-asv-best-scores";

export function readScores(): { ok: true; scores: Record<string, BestScore> } | { ok: false } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ok: true, scores: {} };
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return { ok: true, scores: {} };
    return { ok: true, scores: parsed as Record<string, BestScore> };
  } catch {
    return { ok: false };
  }
}

export function writeBest(
  sectionId: string,
  correct: number,
  total: number,
): { ok: true; improved: boolean; best: BestScore } | { ok: false } {
  const current = readScores();
  if (!current.ok) return { ok: false };
  const prev = current.scores[sectionId];
  const next: BestScore = { correct, total, at: new Date().toISOString() };
  const improved = !prev || (total > 0 && correct / total > prev.correct / prev.total);
  const best = improved ? next : prev;
  if (!best) return { ok: false };
  if (improved) {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ ...current.scores, [sectionId]: next }),
      );
    } catch {
      return { ok: false };
    }
  }
  return { ok: true, improved, best };
}
