from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def export_exercise_docx(exercise: dict) -> bytes:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    h = doc.add_heading("Tabletop Exercise Report", level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Scenario: {exercise.get('scenarioTitle', '')}")
    doc.add_paragraph(f"ID: {exercise.get('id', '')}")
    doc.add_paragraph(f"Completed: {exercise.get('completedAt', '')[:10]}")
    doc.add_paragraph(
        f"Overall Score: {exercise.get('overallPercentage', 0)}%"
    )
    if exercise.get("participants"):
        doc.add_paragraph(
            f"Participants: {', '.join(exercise['participants'])}"
        )

    doc.add_heading("Framework Coverage", level=2)
    doc.add_paragraph(
        "This exercise covers requirements from the following regulatory "
        "frameworks. Refer to each step's details for specific mappings."
    )

    for s in exercise.get("scores", []):
        doc.add_heading(
            f"Step {s['step']}: {s['title']} — {s['percentage']}%", level=2
        )

        doc.add_paragraph(f"Score: {s['score']}/{s['maxScore']}")
        doc.add_paragraph(f"Percentage: {s['percentage']}%")

        response = next(
            (r for r in exercise.get("responses", [])
             if r["step"] == s["step"]),
            None
        )
        if response:
            doc.add_heading("Response", level=3)
            doc.add_paragraph(response.get("answer", ""))

        if s.get("strengths"):
            doc.add_heading("Strengths", level=3)
            for st in s["strengths"]:
                doc.add_paragraph(st, style="List Bullet")

        if s.get("gaps"):
            doc.add_heading("Gaps", level=3)
            for g in s["gaps"]:
                doc.add_paragraph(g, style="List Bullet")

        if s.get("frameworkRequirements"):
            doc.add_heading("Framework Requirements", level=3)
            for fw in s["frameworkRequirements"]:
                doc.add_paragraph(fw, style="List Bullet")

    doc.add_heading("Recommendations", level=2)
    for r in exercise.get("recommendations", []):
        doc.add_paragraph(r, style="List Bullet")

    doc.add_heading("Attestation", level=2)
    doc.add_paragraph(
        "This report serves as audit evidence for incident response "
        "exercises as required by SOC 2 CC7.3, ISO 27001 A.16.1, "
        "NIST 800-53 IR-4, and applicable AI governance frameworks. "
        "The scores reflect automated keyword analysis of participant "
        "responses and should be reviewed alongside expert facilitation notes."
    )

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
