import { useState, useEffect, useRef } from "react";

interface FilterSearchProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
  maxWidth?: string | number;
}

function SearchIcon({ size }: { size?: number }) {
  return (
    <svg
      width={size ?? 14}
      height={size ?? 14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );
}

export default function FilterSearch({
  value,
  onChange,
  placeholder = "Search...",
  debounceMs = 0,
  maxWidth,
}: FilterSearchProps) {
  const [input, setInput] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const initialRef = useRef(true);

  useEffect(() => {
    setInput(value);
  }, [value]);

  useEffect(() => {
    if (initialRef.current) {
      initialRef.current = false;
      return;
    }
    if (debounceMs > 0) {
      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => onChange(input), debounceMs);
      return () => clearTimeout(timerRef.current);
    }
    onChange(input);
  }, [input, debounceMs]);

  return (
    <div className="filter-search" style={maxWidth ? { maxWidth } : undefined}>
      <SearchIcon />
      <input
        type="search"
        value={input}
        onChange={(e): void => setInput(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}
