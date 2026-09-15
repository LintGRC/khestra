import { useState } from "react";
import type { InventoryAsset } from "../api";

const COLUMN_LABELS: Record<string, string> = {
  asset_name: "Asset name",
  asset_type: "Type",
  in_scope: "In scope",
  data_classification: "Data classification",
  owner: "Owner",
  location: "Location",
  notes: "Notes",
};

const COLUMNS = Object.keys(COLUMN_LABELS);

type Props = {
  assets: InventoryAsset[];
  disabled?: boolean;
  onChange: (assets: InventoryAsset[]) => void;
};

export default function InventoryTable({ assets, disabled, onChange }: Props) {
  const [rows, setRows] = useState<InventoryAsset[]>(assets.length ? assets : [{}]);

  const update = (idx: number, col: string, val: string) => {
    const next = rows.map((r, i) => (i === idx ? { ...r, [col]: val } : r));
    setRows(next);
    onChange(next);
  };

  const addRow = () => {
    const next = [...rows, {}];
    setRows(next);
    onChange(next);
  };

  const removeRow = (idx: number) => {
    const next = rows.filter((_, i) => i !== idx);
    setRows(next);
    onChange(next);
  };

  return (
    <div className="inventory-table-wrap">
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th key={col}>{COLUMN_LABELS[col]}</th>
              ))}
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx}>
                {COLUMNS.map((col) => (
                  <td key={col}>
                    {col === "in_scope" ? (
                      <select
                        value={row[col] || ""}
                        onChange={(e) => update(idx, col, e.target.value)}
                        disabled={disabled}
                      >
                        <option value="">—</option>
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={row[col] || ""}
                        onChange={(e) => update(idx, col, e.target.value)}
                        disabled={disabled}
                        placeholder={COLUMN_LABELS[col]}
                      />
                    )}
                  </td>
                ))}
                <td>
                  {!disabled && (
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => removeRow(idx)}
                      title="Remove row"
                    >
                      &times;
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!disabled && (
        <button type="button" className="btn btn-secondary btn-sm" onClick={addRow} style={{ marginTop: 8 }}>
          + Add asset
        </button>
      )}
    </div>
  );
}
