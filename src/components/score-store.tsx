"use client";

import { useCallback, useSyncExternalStore } from "react";
import { writeBest, type BestScore } from "@/lib/scores";

const STORAGE_KEY = "nutrition-asv-best-scores";
const CHANGE_EVENT = "nutrition-asv-scores";

type ScoreState =
  | { status: "loading" }
  | { status: "ready"; scores: Record<string, BestScore> }
  | { status: "error" };

function subscribe(onChange: () => void) {
  window.addEventListener(CHANGE_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(CHANGE_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

function readSnapshot(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "error";
  }
}

function parseSnapshot(raw: string): ScoreState {
  if (raw === "loading") return { status: "loading" };
  if (raw === "error") return { status: "error" };
  if (!raw) return { status: "ready", scores: {} };
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return { status: "ready", scores: {} };
    return { status: "ready", scores: parsed as Record<string, BestScore> };
  } catch {
    return { status: "error" };
  }
}

export function useBestScores() {
  const raw = useSyncExternalStore(subscribe, readSnapshot, () => "loading");
  const state = parseSnapshot(raw);

  const record = useCallback((sectionId: string, correct: number, total: number) => {
    const result = writeBest(sectionId, correct, total);
    window.dispatchEvent(new Event(CHANGE_EVENT));
    return result;
  }, []);

  return { state, record };
}
