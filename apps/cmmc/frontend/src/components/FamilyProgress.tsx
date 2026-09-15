type FamilyRow = {
  family: string;
  total: number;
  met: number;
  reviewed: number;
  open_gaps: number;
  pct: number;
};

export default function FamilyProgress({ rows }: { rows: FamilyRow[] }) {
  if (!rows.length) return null;
  const needsAttention = rows.filter((r) => r.open_gaps > 0).sort((a, b) => b.open_gaps - a.open_gaps);
  const complete = rows.filter((r) => r.open_gaps === 0);

  return (
    <div>
      {needsAttention.length > 0 ? (
        <div className="family-chips">
          {needsAttention.map((r) => (
            <div key={r.family} className="family-chip attention">
              <strong>{r.family}</strong>
              <span>{r.open_gaps} open · {r.met}/{r.total} MET</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">All control families complete — no open SPRS gaps.</p>
      )}
      <table className="family-table" style={{ marginTop: "1rem" }}>
        <thead>
          <tr>
            <th>Family</th>
            <th>MET</th>
            <th>Total</th>
            <th>Open gaps</th>
          </tr>
        </thead>
        <tbody>
          {[...needsAttention, ...complete].map((r) => (
            <tr key={r.family}>
              <td>{r.family}</td>
              <td>{r.met}</td>
              <td>{r.total}</td>
              <td>{r.open_gaps === 0 ? "Complete" : r.open_gaps}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export type { FamilyRow };
