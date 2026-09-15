import { useState, useRef } from "react";
import { apiUrl } from "@shared/apiPrefix";

type Props = {
  frameworkId: string;
  controlId: string;
  onEvidenceCreated?: () => void;
  label?: string;
};

const EVIDENCE_TYPES = [
  { value: "policy", label: "Policy" },
  { value: "certificate", label: "Certificate" },
  { value: "diagram", label: "Diagram" },
  { value: "scan_report", label: "Vulnerability Scan" },
  { value: "training_record", label: "Training Record" },
  { value: "screenshot", label: "Screenshot" },
  { value: "config_export", label: "Configuration Export" },
  { value: "audit_report", label: "Audit Report" },
  { value: "other", label: "Other" },
];

export default function EvidenceUploader({ frameworkId, controlId, onEvidenceCreated, label }: Props) {
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState("");
  const [evidenceType, setEvidenceType] = useState("other");
  const [displayTitle, setDisplayTitle] = useState("");
  const [evidenceVersion, setEvidenceVersion] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setMsg("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("framework_id", frameworkId);
      fd.append("control_id", controlId);
      fd.append("name", file.name);
      fd.append("uploaded_by", "user@company.com");
      fd.append("evidence_type", evidenceType);
      fd.append("display_title", displayTitle || file.name);
      fd.append("evidence_version", evidenceVersion);
      const res = await fetch(apiUrl("/api/evidence-hub/upload-and-map"), { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      setMsg("Uploaded to Evidence Hub.");
      setDisplayTitle("");
      setEvidenceVersion("");
      if (fileRef.current) fileRef.current.value = "";
      onEvidenceCreated?.();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="evidence-upload" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {label && <span className="muted" style={{ fontSize: 11 }}>{label}</span>}
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <input ref={fileRef} type="file" disabled={uploading} accept=".pdf,.png,.jpg,.jpeg,.json,.conf,.txt,.csv" />
        <button className="btn btn-sm btn-primary" disabled={uploading} onClick={handleUpload}>
          {uploading ? "Uploading..." : "Upload to Hub"}
        </button>
        {msg && <span className="muted" style={{ fontSize: 11 }}>{msg}</span>}
      </div>
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <select
          value={evidenceType}
          onChange={(e) => setEvidenceType(e.target.value)}
          style={{ fontSize: 11, padding: "2px 4px" }}
        >
          {EVIDENCE_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Display title (optional)"
          value={displayTitle}
          onChange={(e) => setDisplayTitle(e.target.value)}
          style={{ fontSize: 11, padding: "2px 4px", width: 200 }}
        />
        <input
          type="text"
          placeholder="Version (optional)"
          value={evidenceVersion}
          onChange={(e) => setEvidenceVersion(e.target.value)}
          style={{ fontSize: 11, padding: "2px 4px", width: 80 }}
        />
      </div>
    </div>
  );
}
