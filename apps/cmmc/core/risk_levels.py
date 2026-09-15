"""Risk level from likelihood × impact (POA&M priority)."""

from app_config import IMPACT_LEVELS, LIKELIHOOD_LEVELS

_RISK_MATRIX = {
    ("Low", "Low"): "Low",
    ("Low", "Medium"): "Low",
    ("Low", "High"): "Moderate",
    ("Low", "Critical"): "Moderate",
    ("Medium", "Low"): "Low",
    ("Medium", "Medium"): "Moderate",
    ("Medium", "High"): "High",
    ("Medium", "Critical"): "High",
    ("High", "Low"): "Moderate",
    ("High", "Medium"): "High",
    ("High", "High"): "High",
    ("High", "Critical"): "Critical",
    ("Critical", "Low"): "Moderate",
    ("Critical", "Medium"): "High",
    ("Critical", "High"): "Critical",
    ("Critical", "Critical"): "Critical",
}


def combined_risk_level(likelihood: str, impact: str) -> str:
    return _RISK_MATRIX.get((likelihood, impact), "Moderate")
