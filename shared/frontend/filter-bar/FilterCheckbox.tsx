interface FilterCheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export default function FilterCheckbox({ label, checked, onChange }: FilterCheckboxProps) {
  return (
    <label className="filter-checkbox">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}
