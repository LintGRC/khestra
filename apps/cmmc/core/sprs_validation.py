"""SPRS validation scenarios vs DoW Assessment Methodology (engine self-test)."""

from typing import Any, Dict, List

from controls import CMMC_FRAMEWORK
from sprs_engine import BASE_SCORE, MIN_SCORE, calculate_detailed_sprs

ScenarioResult = Dict[str, Any]


def _all_status(status: str) -> Dict[str, Any]:
    return {cid: {"status": status} for cid in CMMC_FRAMEWORK}


def _scenario(
    scenario_id: str,
    name: str,
    answers: Dict[str, Any],
    expected_score: int,
    notes: str = "",
) -> Dict[str, Any]:
    scoped = list(CMMC_FRAMEWORK.keys())
    actual = calculate_detailed_sprs(answers, scoped)["final_score"]
    return {
        "id": scenario_id,
        "name": name,
        "expected_score": expected_score,
        "actual_score": actual,
        "passed": actual == expected_score,
        "notes": notes,
    }


def get_validation_scenarios() -> List[Dict[str, Any]]:
    """Five fixed scenarios for capstone / product validation."""
    all_met = _all_status("MET")

    one_five = _all_status("MET")
    one_five["AC.L2-3.1.1"] = {"status": "NOT MET"}

    mfa_partial = _all_status("MET")
    mfa_partial["IA.L2-3.5.3"] = {"status": "PARTIALLY MET"}

    mfa_full = _all_status("MET")
    mfa_full["IA.L2-3.5.3"] = {"status": "NOT MET"}

    fips_partial = _all_status("MET")
    fips_partial["SC.L2-3.13.11"] = {"status": "PARTIALLY MET"}

    return [
        _scenario("S1", "All controls MET", all_met, BASE_SCORE, "Perfect score baseline."),
        _scenario("S2", "One 5-point control NOT MET (3.1.1)", one_five, BASE_SCORE - 5),
        _scenario("S3", "MFA partial (3.5.3 PARTIALLY MET)", mfa_partial, BASE_SCORE - 3),
        _scenario("S4", "MFA not implemented (3.5.3 NOT MET)", mfa_full, BASE_SCORE - 5),
        _scenario("S5", "FIPS partial (3.13.11 PARTIALLY MET)", fips_partial, BASE_SCORE - 3),
    ]


def run_validation() -> Dict[str, Any]:
    scenarios = get_validation_scenarios()
    passed = sum(1 for s in scenarios if s["passed"])
    return {
        "total": len(scenarios),
        "passed": passed,
        "all_passed": passed == len(scenarios),
        "scenarios": scenarios,
    }


def format_validation_report() -> str:
    result = run_validation()
    lines = [
        "SPRS Engine Validation Report",
        "DoW NIST SP 800-171 Assessment Methodology (Rev 2 weights)",
        f"Result: {result['passed']}/{result['total']} scenarios passed",
        "",
    ]
    for s in result["scenarios"]:
        status = "PASS" if s["passed"] else "FAIL"
        lines.append(f"[{status}] {s['id']}: {s['name']}")
        lines.append(f"       Expected: {s['expected_score']}  Actual: {s['actual_score']}")
        if s["notes"]:
            lines.append(f"       Notes: {s['notes']}")
        lines.append("")
    return "\n".join(lines)
