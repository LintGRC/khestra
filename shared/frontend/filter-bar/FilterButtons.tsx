interface ButtonItem {
  key: string;
  label: string;
  count?: number;
  color?: string;
}

interface FilterButtonsProps {
  items: ButtonItem[];
  active: string;
  onChange: (key: string) => void;
  label?: string;
}

export default function FilterButtons({ items, active, onChange, label }: FilterButtonsProps) {
  return (
    <>
      {label && <span className="filter-label">{label}</span>}
      <span className="filter-btn-group">
        {items.map((item) => (
          <button
            key={item.key}
            className={`btn btn-sm ${active === item.key ? "btn-primary" : "btn-ghost"}`}
            onClick={() => onChange(item.key)}
            style={active === item.key ? undefined : item.color ? { color: item.color } : undefined}
          >
            {item.label}
            {item.count !== undefined && <span className="filter-badge">{item.count}</span>}
          </button>
        ))}
      </span>
    </>
  );
}
