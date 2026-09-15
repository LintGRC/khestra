import { useEffect, useState } from "react";
import { INVENTORY_COLUMNS } from "../api";

const LABELS: Record<string, string> = {
  asset_name: "Asset name",
  asset_type: "Type",
  in_scope: "In scope",
  cui: "CUI",
  owner: "Owner",
  location: "Location",
  notes: "Notes",
};

type Props = {
  rows: Record<string, string>[];
  onChange: (rows: Record<string, string>[]) => void;
  disabled?: boolean;
  updatedAt?: string;
};

const emptyRow = (): Record<string, string> =>
  Object.fromEntries(INVENTORY_COLUMNS.map((c) => [c, ""]));

export default function InventoryTable({ rows, onChange, disabled, updatedAt }: Props) {
  const [local, setLocal] = useState(rows);

  useEffect(() => {
    setLocal(rows);
  }, [rows]);

  const sync = (next: Record<string, string>[]) => {
    setLocal(next);
    onChange(next);
  };

  const update = (idx: number, col: string, val: string) => {
    const next = local.map((r, i) => (i === idx ? { ...r, [col]: val } : r));
    sync(next);
  };

  const renderCell = (row: Record<string, string>, idx: number, col: string) => {
    if (col === "in_scope" || col === "cui") {
      return (
        <select
          value={row[col] || ""}
          disabled={disabled}
          onChange={(e) => update(idx, col, e.target.value)}
        >
          <option value="">—</option>
          <option value="yes">Yes</option>
          <option value="no">No</option>
        </select>
      );
    }
    return (
      <input
        value={row[col] || ""}
        disabled={disabled}
        onChange={(e) => update(idx, col, e.target.value)}
      />
    );
  };

  return (
    <div className="inventory-table-wrap">
      <p className="muted">
        Optional structured list for your SSP appendix. Import CSV or edit rows — columns: asset_name, asset_type,
        in_scope, cui, owner, location, notes.
      </p>
      {updatedAt && <p className="muted">Last saved: {updatedAt}</p>}
      <table className="inventory-table">
        <thead>
          <tr>
            {INVENTORY_COLUMNS.map((c) => (
              <th key={c}>{LABELS[c] || c}</th>
            ))}
            {!disabled && <th />}
          </tr>
        </thead>
        <tbody>
          {local.map((row, idx) => (
            <tr key={idx}>
              {INVENTORY_COLUMNS.map((c) => (
                <td key={c}>{renderCell(row, idx, c)}</td>
              ))}
              {!disabled && (
                <td>
                  <button
                    type="button"
                    className="btn-link"
                    onClick={() => sync(local.filter((_, i) => i !== idx))}
                  >
                    Remove
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
      {!disabled && (
        <button type="button" className="btn-secondary" style={{ marginTop: "0.5rem" }} onClick={() => sync([...local, emptyRow()])}>
          Add row
        </button>
      )}
    </div>
  );
}

export { INVENTORY_COLUMNS };
