export function pctTone(value: number): "good" | "warn" | "bad" {
  if (value >= 80) return "good";
  if (value >= 50) return "warn";
  return "bad";
}

export function sprsTone(score: number): "good" | "warn" | "bad" {
  if (score >= 80) return "good";
  if (score >= 50) return "warn";
  return "bad";
}

export function gapTone(gaps: number): "good" | "warn" | "bad" {
  if (gaps === 0) return "good";
  if (gaps <= 8) return "warn";
  return "bad";
}

export function exportTone(pct: number): "good" | "warn" | "bad" {
  if (pct >= 70) return "good";
  if (pct >= 40) return "warn";
  return "bad";
}
