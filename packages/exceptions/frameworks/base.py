from dataclasses import dataclass, field


@dataclass
class FrameworkConfig:
    name: str
    display_name: str
    states: list[str]
    transitions: dict[str, list[str]]

    def validate_transition(self, from_status: str, to_status: str) -> bool:
        allowed = self.transitions.get(from_status, [])
        return to_status in allowed

    def allowed_transitions(self, from_status: str) -> list[str]:
        return self.transitions.get(from_status, [])

    def score(self, likelihood: int, impact: int) -> dict:
        score_val = likelihood * impact
        if score_val >= 15:
            level = "critical"
        elif score_val >= 10:
            level = "high"
        elif score_val >= 5:
            level = "medium"
        else:
            level = "low"
        color_map = {"critical": "#b91c1c", "high": "#dc2626", "medium": "#a16207", "low": "#15803d"}
        return {
            "score": score_val,
            "likelihood": likelihood,
            "impact": impact,
            "level": level,
            "color": color_map.get(level, "#64748b"),
        }
