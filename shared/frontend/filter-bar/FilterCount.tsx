interface FilterCountProps {
  value: number;
  label?: string;
}

export default function FilterCount({ value, label = "item" }: FilterCountProps) {
  return (
    <span className="filter-count">
      {value} {label}{value !== 1 ? "s" : ""}
    </span>
  );
}
