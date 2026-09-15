import re

STOP_WORDS = {"was", "were", "the", "a", "an", "is", "are", "be", "been",
              "in", "on", "at", "to", "of", "for", "and", "or", "did",
              "has", "had", "have", "does", "do"}

ACTION_INDICATORS = [
    "notify", "contact", "call", "email", "engage", "activate",
    "deploy", "implement", "isolate", "contain", "revoke",
    "reset", "rotate", "review", "audit", "restore", "rebuild",
    "test", "verify", "document", "preserve", "collect", "secure",
]


def _extract_keywords(criterion: str) -> list[str]:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", criterion.lower())
    return [w for w in cleaned.split() if len(w) > 2 and w not in STOP_WORDS]


def _has_specific_actions(answer: str) -> bool:
    lower = answer.lower()
    return any(a in lower for a in ACTION_INDICATORS)


def score_step(step: dict, answer: str) -> dict:
    criteria = step["scoringCriteria"]
    answer_lower = answer.lower()
    max_score = len(criteria) * 2
    score = 0
    strengths: list[str] = []
    gaps: list[str] = []

    for criterion in criteria:
        keywords = _extract_keywords(criterion)
        matched = sum(1 for kw in keywords if kw in answer_lower)
        total = max(len(keywords), 1)
        partial = matched / total
        points = 2 if partial >= 0.6 else (1 if partial >= 0.3 else 0)
        score += points
        if points >= 2:
            strengths.append(criterion)
        elif points == 0:
            gaps.append(criterion)

    if len(answer) > 200:
        score = min(max_score, score + 1)
    if _has_specific_actions(answer):
        score = min(max_score, score + 1)

    percentage = round((score / max_score) * 100) if max_score else 0

    return {
        "step": step["step"],
        "title": step["title"],
        "score": score,
        "maxScore": max_score,
        "percentage": percentage,
        "strengths": strengths[:3],
        "gaps": gaps[:3],
        "frameworkRequirements": step.get("frameworkRefs", []),
    }


def calculate_overall(scores: list[dict]) -> int:
    if not scores:
        return 0
    return round(sum(s["percentage"] for s in scores) / len(scores))


def generate_recommendations(scores: list[dict]) -> list[str]:
    recs: list[str] = []

    all_gaps = [g for s in scores for g in s["gaps"]]
    gap_counts: dict[str, int] = {}
    for g in all_gaps:
        gap_counts[g] = gap_counts.get(g, 0) + 1
    recurring = [g for g, c in gap_counts.items() if c >= 2]
    if recurring:
        recs.append(
            f"Multiple steps missed the following considerations. "
            f"Review and strengthen: {'; '.join(recurring)}"
        )

    weak = [s for s in scores if s["percentage"] < 50]
    if weak:
        recs.append(
            f"Steps needing most improvement: "
            f"{', '.join(s['title'] for s in weak)}. "
            f"Revisit the expert guidance for these areas."
        )

    overall = sum(s["percentage"] for s in scores) / len(scores) if scores else 0
    if overall < 70:
        recs.append(
            "Overall score below 70%. Consider re-running this scenario "
            "after reviewing the expert guidance for each step."
        )

    recs.append(
        "Conduct tabletop exercises at least annually as required by "
        "SOC 2 CC7.3, ISO 27001 A.16.1, and NIST 800-53 IR-4."
    )
    recs.append(
        "Document your incident response plan updates based on "
        "findings from this exercise."
    )
    recs.append(
        "Share results with leadership and incorporate lessons learned "
        "into your security awareness program."
    )

    return recs
