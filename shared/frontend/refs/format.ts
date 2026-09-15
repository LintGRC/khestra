// Canonical framework-reference display formatting (TS mirror of packages/refs/format.py).

const FRAMEWORK_LABELS: Record<string, string> = {
  "EU AI Act": "EU AI Act",
  "NIST AI RMF": "NIST AI RMF",
  "ISO 42001": "ISO 42001",
  "OWASP Agentic": "OWASP Agentic",
  "CMMC": "CMMC",
  "SOC 2": "SOC 2",
  "ISO 27001": "ISO 27001",
};

const ANNEX_CLAUSE = /^A\.\d+$/;

export function displayClause(framework: string, clause: string): string {
  const label = FRAMEWORK_LABELS[framework] ?? framework;
  const text = (clause ?? "").trim();
  if (!text || text.startsWith(label)) return text;
  if (framework === "ISO 42001") {
    const parts = text
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean)
      .map((p) => (ANNEX_CLAUSE.test(p) ? `Annex ${p}` : p));
    return `${label} ${parts.join(", ")}`;
  }
  if (framework === "ISO 27001") {
    const parts = text
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean)
      .map((p) => (ANNEX_CLAUSE.test(p) ? `Annex ${p}` : p));
    return `${label} ${parts.join(", ")}`;
  }
  return `${label} ${text}`;
}

function frameworkFromId(controlId: string): string {
  if (controlId.startsWith("EU-")) return "EU AI Act";
  if (controlId.startsWith("NIST-")) return "NIST AI RMF";
  if (controlId.startsWith("ISO-A.") || controlId.startsWith("ISO-")) return "ISO 42001";
  if (controlId.startsWith("ISO27K-")) return "ISO 27001";
  if (controlId.startsWith("OWASP-LLM-")) return "OWASP LLM Top 10";
  if (controlId.startsWith("OWASP-")) return "OWASP Agentic";
  if (controlId.includes(".L")) return "CMMC";
  if (controlId.startsWith("SOC-") || controlId.startsWith("CC")) return "SOC 2";
  return "";
}

export function renderControlRef(controlId: string): string {
  const cid = (controlId ?? "").trim();
  const framework = frameworkFromId(cid);
  if (framework === "EU AI Act") return `EU AI Act Art. ${cid.slice(3)}`;
  if (framework === "NIST AI RMF") return `NIST AI RMF ${cid.slice(5).replace("-", " ")}`;
  if (framework === "ISO 42001") {
    const clause = cid.slice(4);
    return clause.startsWith("A.") ? `ISO 42001 Annex ${clause}` : `ISO 42001 Clause ${clause}`;
  }
  if (framework === "ISO 27001") {
    const clause = cid.replace("ISO27K-", "");
    return clause.startsWith("A.") ? `ISO 27001 Annex ${clause}` : `ISO 27001 ${clause}`;
  }
  if (framework === "OWASP Agentic") return `OWASP ASI${String(parseInt(cid.slice(6), 10)).padStart(2, "0")}`;
  if (framework === "OWASP LLM Top 10") return `OWASP LLM${String(parseInt(cid.slice(10), 10)).padStart(2, "0")}:2025`;
  if (framework === "CMMC") return `CMMC ${cid}`;
  if (framework === "SOC 2") return `SOC 2 ${cid}`;
  return cid;
}
