export type BestScore = {
  correct: number;
  total: number;
  at: string;
};

const STORAGE_KEY = "studyweb-best-scores";
const LEGACY_KEY = "nutrition-asv-best-scores";
const LEGACY_COURSE = "nutrition-asv";

export function scoreKey(courseId: string, sectionId: string): string {
  return `${courseId}:${sectionId}`;
}

function migrateLegacy(raw: string): string {
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return "";
    const next: Record<string, BestScore> = {};
    for (const [sectionId, score] of Object.entries(parsed as Record<string, BestScore>)) {
      if (!score || typeof score !== "object") continue;
      next[scoreKey(LEGACY_COURSE, sectionId)] = score;
    }
    return JSON.stringify(next);
  } catch {
    return "";
  }
}

/** Raw JSON of all course scores, or "" / "error". Does not write during read. */
export function readStored(): string {
  try {
    const current = localStorage.getItem(STORAGE_KEY);
    if (current !== null) return current;
    const legacy = localStorage.getItem(LEGACY_KEY);
    if (!legacy) return "";
    return migrateLegacy(legacy);
  } catch {
    return "error";
  }
}

function parseScores(raw: string): Record<string, BestScore> {
  if (!raw) return {};
  const parsed: unknown = JSON.parse(raw);
  if (!parsed || typeof parsed !== "object") return {};
  return parsed as Record<string, BestScore>;
}

export function readScores():
  | { ok: true; scores: Record<string, BestScore> }
  | { ok: false } {
  const raw = readStored();
  if (raw === "error") return { ok: false };
  try {
    return { ok: true, scores: parseScores(raw) };
  } catch {
    return { ok: false };
  }
}

export function writeBest(
  id: string,
  correct: number,
  total: number,
): { ok: true; improved: boolean; best: BestScore } | { ok: false } {
  const current = readScores();
  if (!current.ok) return { ok: false };
  const prev = current.scores[id];
  const next: BestScore = { correct, total, at: new Date().toISOString() };
  const improved = !prev || (total > 0 && correct / total > prev.correct / prev.total);
  const best = improved ? next : prev;
  if (!best) return { ok: false };
  if (improved) {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ ...current.scores, [id]: next }),
      );
    } catch {
      return { ok: false };
    }
  }
  return { ok: true, improved, best };
}
