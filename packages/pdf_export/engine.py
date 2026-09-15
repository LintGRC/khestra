from __future__ import annotations

import logging
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

from fpdf import FPDF
from fpdf.errors import FPDFException

_logger = logging.getLogger(__name__)


class ReportPDF(FPDF):
    _SAFE_REPLACEMENTS = str.maketrans({
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2022": "-",  # bullet
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",  # non-breaking space
    })

    @staticmethod
    def _sanitize(text: str) -> str:
        if isinstance(text, str):
            return text.translate(ReportPDF._SAFE_REPLACEMENTS)
        return str(text)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 7)
            self.cell(0, 5, "Compliance Report", align="L")
            self.cell(0, 5, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.line(10, 12, self.w - self.r_margin, 12)
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.cell(0, 10, f"Generated {getattr(self, '_generated_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}", align="C")

    def section_heading(self, title: str, level: int = 1):
        if not title:
            return
        sizes = {0: 16, 1: 13, 2: 11}
        self.set_font("Helvetica", "B", sizes.get(level, 10))
        self.set_text_color(31, 78, 121)
        self.cell(0, 8, self._sanitize(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text: str):
        if not text:
            return
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, self._sanitize(text))
        self.ln(1)

    def bullet(self, text: str):
        if not text:
            return
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        try:
            if self.get_x() > self.w - self.r_margin - 15:
                self.ln()
            self.set_x(self.l_margin + 5)
            self.cell(4, 5, "- ")
            self.multi_cell(0, 5, self._sanitize(text))
        except Exception:
            self.set_x(self.l_margin + 5)
            cleaned = self._sanitize(text).replace("\n", " ").strip()[:100]
            self.multi_cell(0, 5, cleaned)

    def kv_row(self, key: str, value: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(50, 50, 50)
        self.cell(50, 5, self._sanitize(key))
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, self._sanitize(value), new_x="LMARGIN", new_y="NEXT")

    def bar_chart(
        self,
        title: str,
        labels: List[str],
        values: List[float],
        bar_color: tuple = (31, 78, 121),
        value_suffix: str = "",
    ):
        """Simple horizontal-bar chart via fpdf2 primitives."""
        if not labels or not values:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(50, 50, 50)
        max_val = max(values) or 1
        scale = (self.w - self.l_margin - self.r_margin - 70) / max_val
        for label, value in zip(labels, values):
            bar_w = max(2.0, value * scale)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(50, 50, 50)
            self.cell(62, 6, self._sanitize(str(label))[:34])
            self.set_fill_color(*bar_color)
            self.rect(self.get_x(), self.get_y() + 1, bar_w, 4, style="F")
            self.set_font("Helvetica", "B", 8)
            self.cell(0, 6, f" {self._sanitize(str(value))}{value_suffix}", new_x="LMARGIN", new_y="NEXT")
            self.ln(0.5)


def generate_pdf(title: str, sections: List[Dict[str, Any]]) -> bytes:
    pdf = ReportPDF()
    pdf._generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 12, pdf._sanitize(title), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for section in sections:
        stype = section.get("type", "text")
        content = section.get("content") or ""

        if stype == "heading":
            level = section.get("level", 1)
            if not isinstance(level, int):
                level = 1
            pdf.section_heading(content, level)
        elif stype == "text":
            pdf.body_text(content)
        elif stype == "bullet":
            pdf.bullet(content)
        elif stype == "kv":
            pdf.kv_row(section.get("key") or "", section.get("value") or "")
        elif stype == "page_break":
            pdf.add_page()
        elif stype == "table":
            headers = section.get("headers", [])
            rows = section.get("rows", [])
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(31, 78, 121)
            pdf.set_text_color(255, 255, 255)
            for h in headers:
                pdf.cell(35, 6, pdf._sanitize(h), border=1, fill=True)
            pdf.ln()
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(50, 50, 50)
            for row in rows:
                for cell in row:
                    pdf.cell(35, 5, pdf._sanitize(str(cell)[:20]), border=1)
                pdf.ln()
        elif stype == "barchart":
            pdf.bar_chart(
                section.get("title", ""),
                section.get("labels", []),
                section.get("values", []),
                bar_color=section.get("bar_color", (31, 78, 121)),
                value_suffix=section.get("value_suffix", ""),
            )
        else:
            _logger.warning("Unknown section type: %s", stype)

    with BytesIO() as out:
        pdf.output(out)
        return out.getvalue()
