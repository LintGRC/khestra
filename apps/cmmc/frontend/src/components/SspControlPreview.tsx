import { useMemo } from "react";
import { ControlDetail } from "../api";
import { buildControlSspPreview } from "../lib/sspPreview";

type Props = {
  control: ControlDetail;
  form: Partial<ControlDetail>;
};

export default function SspControlPreview({ control, form }: Props) {
  const preview = useMemo(() => buildControlSspPreview(control, form), [control, form]);

  return (
    <div className="panel ssp-preview-panel">
      <div className="panel-header">
        <strong>SSP preview</strong>
        <span className="muted">Section {preview.family_section}</span>
      </div>
      <div className="panel-body ssp-preview-body">
        <p className="muted ssp-preview-note">{preview.export_note}</p>

        <article className="ssp-preview-doc">
          <p className="ssp-preview-breadcrumb muted">
            5. Security Requirements → {preview.family_section}
          </p>
          <h3 className="ssp-preview-heading">{preview.heading}</h3>

          <table className="ssp-preview-attrs">
            <tbody>
              {preview.attributes.map((row) => (
                <tr key={row.label}>
                  <th>{row.label}</th>
                  <td>{row.value}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="ssp-preview-block">
            <h4>Description</h4>
            <p className={preview.description_missing ? "ssp-preview-missing" : undefined}>
              {preview.description}
            </p>
            {preview.placeholders.length > 0 && (
              <p className="field-hint ssp-placeholder-hint">
                Replace before export:{" "}
                {preview.placeholders.map((ph, i) => (
                  <span key={ph}>
                    {i > 0 && ", "}
                    <mark className="ssp-placeholder">{ph}</mark>
                  </span>
                ))}
              </p>
            )}
          </div>

          {preview.assessment_methods.length > 0 && (
            <div className="ssp-preview-block">
              <h4>Assessment methods</h4>
              <p>{preview.assessment_methods.join("; ")}</p>
            </div>
          )}

          {preview.evidence_files.length > 0 && (
            <div className="ssp-preview-block">
              <h4>Attached evidence files</h4>
              <ul className="guidance-list">
                {preview.evidence_files.map((ev) => (
                  <li key={ev.filename}>
                    {ev.filename}
                    {ev.upload_date ? ` (uploaded ${ev.upload_date.slice(0, 10)})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </article>
      </div>
    </div>
  );
}
