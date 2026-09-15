import type { ReactNode } from "react";

interface FilterBarProps {
  children: ReactNode;
  className?: string;
}

export default function FilterBar({ children, className = "" }: FilterBarProps) {
  return <div className={`filter-bar ${className}`}>{children}</div>;
}
