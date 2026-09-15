QUESTIONNAIRE = {
    "id": "default",
    "title": "Vendor Security Intake",
    "version": "1.0",
    "sections": [
        {
            "id": "vendor_overview",
            "title": "Vendor Overview",
            "weight": 20,
            "questions": [
                {"id": "q1", "type": "text", "label": "Company name and headquarters location", "required": True},
                {"id": "q2", "type": "text", "label": "Describe the products/services provided", "required": True},
                {"id": "q3", "type": "text", "label": "List key personnel and their roles", "required": False},
            ],
        },
        {
            "id": "data_handling",
            "title": "Data Handling & Privacy",
            "weight": 35,
            "questions": [
                {"id": "q4", "type": "select", "label": "Where will our data be stored/processed?",
                 "options": ["US Only", "EU/EEA", "Global", "Other"], "required": True},
                {"id": "q5", "type": "select", "label": "What types of data will be accessed?",
                 "options": ["Public", "Internal", "Confidential", "Restricted/PII"], "required": True},
            ],
        },
        {
            "id": "security_controls",
            "title": "Security Controls",
            "weight": 30,
            "questions": [
                {"id": "q6", "type": "text", "label": "Describe your security certifications and controls", "required": True},
            ],
        },
        {
            "id": "contractual",
            "title": "Contractual Requirements",
            "weight": 15,
            "questions": [
                {"id": "q7", "type": "select", "label": "Do you have a SOC 2 report?",
                 "options": ["Yes - Type II", "Yes - Type I", "In Progress", "No"], "required": True},
                {"id": "q8", "type": "select", "label": "Do you have Cyber/Data Breach Insurance?",
                 "options": ["Yes", "No"], "required": True},
            ],
        },
    ],
}


def get_questionnaire(qid: str = "default") -> dict:
    return QUESTIONNAIRE


VAGUE_PATTERNS: list[str] = [
    "as per industry standards", "in accordance with best practices",
    "we follow standard procedures", "generally accepted", "to the extent possible",
    "subject to", "depending on", "as applicable", "where required",
    "we reserve the right", "may vary", "upon request",
    "please refer to", "we are committed to", "we strive to",
    "robust", "comprehensive", "state-of-the-art", "cutting-edge",
    "industry-leading", "best-in-class", "world-class",
]


def analyze_answers(answers: list[dict]) -> dict:
    results = []
    for a in answers:
        qid = a.get("id", a.get("questionId", ""))
        val = str(a.get("value", ""))
        if len(val.strip()) < 30:
            results.append({"questionId": qid, "issue": "Too short or empty", "severity": "medium"})
            continue
        lower = val.lower()
        matches = [p for p in VAGUE_PATTERNS if p in lower]
        if matches:
            results.append({"questionId": qid, "issue": "Vague language detected", "severity": "low", "matches": matches})
    return {
        "total_questions_analyzed": len(answers),
        "issues_found": len(results),
        "results": results,
    }


def prefill_from_soc2(text: str) -> list[dict]:
    """Parse a SOC 2 report text and return pre-filled answers."""
    lower = text.lower()
    answers = []

    # q4: data residency
    if "us" in lower or "united states" in lower:
        answers.append({"id": "q4", "value": "US Only"})
    elif "eu" in lower or "europe" in lower or "germany" in lower:
        answers.append({"id": "q4", "value": "EU/EEA"})
    else:
        answers.append({"id": "q4", "value": "US Only"})

    # q5: data types accessed
    if "pii" in lower or "personally identifiable" in lower:
        answers.append({"id": "q5", "value": "Restricted/PII"})
    elif "confidential" in lower:
        answers.append({"id": "q5", "value": "Confidential"})
    elif "internal" in lower:
        answers.append({"id": "q5", "value": "Internal"})
    else:
        answers.append({"id": "q5", "value": "Internal"})

    # q7: SOC 2 report type
    if "type ii" in lower:
        answers.append({"id": "q7", "value": "Yes - Type II"})
    elif "type i" in lower:
        answers.append({"id": "q7", "value": "Yes - Type I"})
    elif "in progress" in lower or "ongoing" in lower:
        answers.append({"id": "q7", "value": "In Progress"})
    else:
        answers.append({"id": "q7", "value": "Yes - Type II"})

    # q8: insurance
    if "insurance" in lower and ("cyber" in lower or "breach" in lower):
        answers.append({"id": "q8", "value": "Yes"})

    # q6: security controls - extract relevant sentence
    sec_sentences = []
    for keyword in ["access control", "encryption", "firewall", "intrusion detection",
                     "vulnerability", "penetration test", "audit log", "incident response",
                     "backup", "disaster recovery", "sso", "mfa", "authentication"]:
        for sentence in text.split("."):
            if keyword in sentence.lower() and sentence.strip():
                sec_sentences.append(sentence.strip())
    if sec_sentences:
        summary = ". ".join(sec_sentences[:5])[:500]
        answers.append({"id": "q6", "value": summary})
    else:
        ct = text[:300].strip()
        answers.append({"id": "q6", "value": ct or "SOC 2 report uploaded"})

    # q1: company name
    for line in text.splitlines():
        line = line.strip()
        if line and ("inc" in line.lower() or "llc" in line.lower() or "corp" in line.lower() or "ltd" in line.lower()):
            answers.append({"id": "q1", "value": line[:100]})
            break
    if not any(a["id"] == "q1" for a in answers):
        answers.append({"id": "q1", "value": "See SOC 2 report"})

    # q2: products/services
    if "service" in lower or "product" in lower or "platform" in lower:
        for line in text.splitlines():
            if ("service" in line.lower() or "product" in line.lower()) and len(line) > 20:
                answers.append({"id": "q2", "value": line[:200]})
                break
    if not any(a["id"] == "q2" for a in answers):
        answers.append({"id": "q2", "value": "See SOC 2 report"})

    return answers


def score_response(answers: list[dict]) -> dict:
    answer_map = {a.get("id", ""): a.get("value", "") for a in answers}

    category_scores = {}
    findings = []

    def _q_score(qid: str, good_values: list[str], bad_values: list[str]) -> tuple[int, str | None]:
        val = answer_map.get(qid, "")
        if val in good_values:
            return 100, None
        elif val in bad_values:
            return 0, f"{qid}: Answer '{val}' indicates elevated risk"
        return 50, None

    # Vendor overview: 100 = answered, 0 = empty
    overview_score = 100
    for qid in ("q1", "q2"):
        if not answer_map.get(qid, "").strip():
            overview_score -= 50
    if overview_score < 0:
        overview_score = 0
    category_scores["vendor_overview"] = overview_score

    # Data handling
    dh_score = 0
    dh_items = 0
    q4_score, q4_finding = _q_score("q4", ["US Only", "EU/EEA"], ["Global", "Other"])
    dh_score += q4_score
    dh_items += 1
    if q4_finding:
        findings.append({"id": "f4", "question": "q4", "description": q4_finding, "severity": "medium"})

    q5_score, q5_finding = _q_score("q5", ["Public", "Internal"], ["Confidential", "Restricted/PII"])
    dh_score += q5_score
    dh_items += 1
    if q5_finding:
        findings.append({"id": "f5", "question": "q5", "description": q5_finding, "severity": "high"})

    category_scores["data_handling"] = round(dh_score / max(dh_items, 1))

    # Security controls
    sec_score = 100 if answer_map.get("q6", "").strip() else 0
    category_scores["security_controls"] = sec_score
    if sec_score < 100:
        findings.append({"id": "f6", "question": "q6", "description": "No security controls description provided", "severity": "high"})

    # Contractual
    con_score = 0
    con_items = 0
    q7_score, q7_finding = _q_score("q7", ["Yes - Type II", "Yes - Type I"], ["In Progress", "No"])
    con_score += q7_score
    con_items += 1
    if q7_finding:
        findings.append({"id": "f7", "question": "q7", "description": q7_finding, "severity": "high"})

    q8_score, q8_finding = _q_score("q8", ["Yes"], ["No"])
    con_score += q8_score
    con_items += 1
    if q8_finding:
        findings.append({"id": "f8", "question": "q8", "description": q8_finding, "severity": "medium"})

    category_scores["contractual"] = round(con_score / max(con_items, 1))

    # Weighted overall
    weights = {s["id"]: s["weight"] for s in QUESTIONNAIRE["sections"]}
    total_weight = sum(weights.values())
    overall = sum(category_scores.get(cid, 0) * w for cid, w in weights.items()) / max(total_weight, 1)
    overall_score = round(overall)

    # Risk level
    if overall_score >= 80:
        overall_level = "low"
    elif overall_score >= 60:
        overall_level = "medium"
    elif overall_score >= 40:
        overall_level = "high"
    else:
        overall_level = "critical"

    return {
        "overallScore": overall_score,
        "overallLevel": overall_level,
        "categoryScores": category_scores,
        "findings": findings,
    }
