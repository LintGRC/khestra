import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { Upload, CheckCircle, AlertTriangle, Save, Loader } from "lucide-react";

const FRAMEWORKS = [
  { id: "cmmc", prefix: "/api/cmmc" },
  { id: "soc2", prefix: "/api/soc2" },
  { id: "aigovernance", prefix: "/api/ai-governance" },
];

interface Question {
  id: string;
  type: string;
  label: string;
  required?: boolean;
  options?: string[];
}

interface Section {
  id: string;
  title: string;
  weight?: number;
  questions: Question[];
}

interface Questionnaire {
  id: string;
  title: string;
  version: string;
  sections: Section[];
}

async function discoverFramework(vid: string, token: string): Promise<string> {
  const results = await Promise.allSettled(
    FRAMEWORKS.map((fw) =>
      fetch(`${fw.prefix}/vendors/${vid}?token=${encodeURIComponent(token)}`)
        .then((r) => (r.ok ? fw.prefix : null))
    )
  );
  for (const r of results) {
    if (r.status === "fulfilled" && r.value) return r.value;
  }
  throw new Error("Vendor not found");
}

export function VendorQuestionnairePortal() {
  const { vid } = useParams<{ vid: string }>();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [API, setAPI] = useState<string | null>(null);
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [vendorName, setVendorName] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [soc2Uploading, setSoc2Uploading] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const answersRef = useRef(answers);
  answersRef.current = answers;

  const autoSave = useCallback(async () => {
    if (!vid || submitted || !API) return;
    setSaving(true);
    try {
      const ansList = Object.entries(answersRef.current).map(([id, value]) => ({ id, value }));
      const url = `${API}/vendors/response/draft?token=${encodeURIComponent(token)}`;
      await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vendor_id: vid, answers: ansList, questionnaire_id: "default" }),
      });
      setLastSaved(new Date());
    } catch {
      /* silent */
    }
    setSaving(false);
  }, [vid, token, submitted, API]);

  useEffect(() => {
    if (!vid || !token) return;
    setLoading(true);
    setError("");
    discoverFramework(vid, token)
      .then((prefix) => {
        setAPI(prefix);
        return Promise.all([
          fetch(`${prefix}/vendors/questionnaire/default`).then((r) => r.json()),
          fetch(`${prefix}/vendors/${vid}?token=${encodeURIComponent(token)}`).then((r) => r.json()).catch(() => ({ vendor: null })),
          fetch(`${prefix}/vendors/${vid}/response?token=${encodeURIComponent(token)}`).then((r) => r.json()).catch(() => ({ response: null })),
        ]);
      })
      .then(([qData, vData, rData]) => {
        setQuestionnaire(qData.questionnaire);
        setVendorName(vData.vendor?.name || "Vendor");
        if (rData.response?.answers) {
          const ans: Record<string, string> = {};
          for (const a of rData.response.answers) {
            ans[a.id || a.questionId] = a.value || "";
          }
          setAnswers(ans);
        }
        if (rData.response?.status === "submitted") {
          setSubmitted(true);
        }
      })
      .catch(() => setError("Failed to load questionnaire"))
      .finally(() => setLoading(false));
  }, [vid, token]);

  const handleAnswer = (qid: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [qid]: value }));
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(autoSave, 1500);
  };

  useEffect(() => {
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, []);

  async function handleSubmit() {
    if (!vid || !API) return;
    const ansList = Object.entries(answers).map(([id, value]) => ({ id, value }));
    try {
      const url = `${API}/vendors/response/submit?token=${encodeURIComponent(token)}`;
      await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vendor_id: vid, answers: ansList, questionnaire_id: "default" }),
      });
      setSubmitted(true);
    } catch {
      setError("Failed to submit. Please try again.");
    }
  }

  async function handleSoc2Upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !vid || !API) return;
    setSoc2Uploading(true);
    try {
      const form = new FormData();
      form.append("vendor_id", vid);
      form.append("file", file);
      const r = await fetch(`${API}/vendors/questionnaire/upload-soc2`, { method: "POST", body: form });
      const d = await r.json();
      if (d.prefilled_answers) {
        const newAnswers = { ...answers };
        for (const a of d.prefilled_answers) {
          if (a.id && a.value) newAnswers[a.id] = a.value;
        }
        setAnswers(newAnswers);
        autoSave();
      }
    } catch {
      /* silent */
    }
    setSoc2Uploading(false);
    e.target.value = "";
  }

  const allRequiredFilled = questionnaire
    ? questionnaire.sections.every((s) =>
        s.questions
          .filter((q) => q.required)
          .every((q) => (answers[q.id] || "").trim().length > 0)
      )
    : false;

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh", flexDirection: "column", gap: 12 }}>
        <Loader size={24} className="spin" />
        <span className="muted" style={{ fontSize: 13 }}>Loading questionnaire...</span>
      </div>
    );
  }

  if (error) {
    return <div className="panel" style={{ padding: 24, textAlign: "center", color: "var(--danger)" }}><AlertTriangle size={24} /><p>{error}</p></div>;
  }

  if (submitted) {
    return (
      <div style={{ maxWidth: 500, margin: "40px auto", textAlign: "center" }}>
        <div className="panel" style={{ padding: 32 }}>
          <CheckCircle size={48} style={{ color: "var(--success)", margin: "0 auto 16px", display: "block" }} />
          <h2 style={{ margin: "0 0 8px" }}>Thank You</h2>
          <p className="muted" style={{ margin: "0 0 4px" }}>Your questionnaire has been submitted successfully.</p>
          <p className="muted" style={{ fontSize: 12 }}>The review team will follow up if needed.</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 700, margin: "0 auto" }}>
      <div className="panel" style={{ padding: 20, marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em", color: "var(--primary)", marginBottom: 4 }}>
              Vendor Security Intake
            </div>
            <h1 style={{ fontSize: 18, fontWeight: 600, margin: 0 }}>{vendorName}</h1>
            <p className="muted" style={{ fontSize: 12, margin: "4px 0 0" }}>Please complete all required fields. Your progress is auto-saved.</p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
            {saving ? (
              <><Loader size={12} className="spin" /> Saving...</>
            ) : lastSaved ? (
              <><Save size={12} style={{ color: "var(--success)" }} /> Saved {lastSaved.toLocaleTimeString()}</>
            ) : null}
          </div>
        </div>
      </div>

      <div className="panel" style={{ padding: "12px 16px", marginBottom: 16, display: "flex", alignItems: "center", gap: 12, background: "var(--info-soft)" }}>
        <Upload size={16} style={{ color: "var(--primary)" }} />
        <span style={{ fontSize: 12, flex: 1 }}>Upload a SOC 2 report to pre-fill answers automatically.</span>
        <button className="btn btn-secondary btn-sm" disabled={soc2Uploading} onClick={() => document.getElementById("soc2-upload")?.click()}>
          {soc2Uploading ? "Uploading..." : "Upload SOC 2"}
        </button>
        <input id="soc2-upload" type="file" accept=".pdf,.doc,.docx,.txt" hidden onChange={handleSoc2Upload} />
      </div>

      {questionnaire?.sections.map((section) => {
        const sectionAnswers = section.questions.map((q) => answers[q.id] || "");
        const filled = sectionAnswers.filter((a) => a.trim().length > 0).length;
        return (
          <div key={section.id} className="panel" style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div>
                <h3 style={{ fontSize: 14, fontWeight: 600, margin: 0 }}>{section.title}</h3>
              </div>
              <span style={{ fontSize: 11, color: "var(--muted)" }}>{filled}/{section.questions.length}</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {section.questions.map((q) => (
                <div key={q.id}>
                  <label style={{ fontSize: 12, fontWeight: 500, display: "block", marginBottom: 4 }}>
                    {q.label}
                    {q.required && <span style={{ color: "var(--danger)" }}> *</span>}
                  </label>
                  {q.type === "select" && q.options ? (
                    <select
                      value={answers[q.id] || ""}
                      onChange={(e) => handleAnswer(q.id, e.target.value)}
                      style={{ width: "100%" }}
                    >
                      <option value="">-- Select --</option>
                      {q.options.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <textarea
                      value={answers[q.id] || ""}
                      onChange={(e) => handleAnswer(q.id, e.target.value)}
                      rows={3}
                      style={{ width: "100%", resize: "vertical" }}
                      placeholder="Type your answer..."
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}

      <div className="panel" style={{ padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 12, color: "var(--muted)" }}>
          {allRequiredFilled ? (
            <span style={{ color: "var(--success)" }}><CheckCircle size={12} /> All required fields complete</span>
          ) : (
            <span style={{ color: "var(--warning)" }}><AlertTriangle size={12} /> Some required fields are empty</span>
          )}
        </div>
        <button className="btn btn-primary" disabled={!allRequiredFilled} onClick={handleSubmit}>
          Submit Questionnaire
        </button>
      </div>
    </div>
  );
}
