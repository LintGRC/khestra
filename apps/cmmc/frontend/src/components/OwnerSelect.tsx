type Props = {
  id: string;
  label: string;
  value: string;
  teamMembers: string[];
  disabled?: boolean;
  onChange: (value: string) => void;
};

export default function OwnerSelect({ id, label, value, teamMembers, disabled, onChange }: Props) {
  const inRoster = value && teamMembers.some((m) => m.toLowerCase() === value.toLowerCase());
  const selectValue = inRoster ? value : value ? "__custom__" : "";

  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        value={selectValue}
        disabled={disabled}
        onChange={(e) => {
          const v = e.target.value;
          if (v === "__custom__") {
            if (!value || inRoster) onChange("");
            return;
          }
          onChange(v);
        }}
      >
        <option value="">Unassigned</option>
        {teamMembers.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
        <option value="__custom__">Other…</option>
      </select>
      {(selectValue === "__custom__" || (value && !inRoster)) && (
        <input
          className="owner-custom-input"
          value={value}
          disabled={disabled}
          placeholder="Name"
          onChange={(e) => onChange(e.target.value)}
        />
      )}
    </div>
  );
}
