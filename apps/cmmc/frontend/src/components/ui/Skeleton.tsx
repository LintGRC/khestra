import type { CSSProperties, ReactNode } from "react";

type BlockProps = {
  className?: string;
  style?: CSSProperties;
};

export function SkeletonBlock({ className = "", style }: BlockProps) {
  return <div className={`skeleton ${className}`.trim()} style={style} aria-hidden="true" />;
}

type LineProps = BlockProps & {
  size?: "sm" | "md" | "lg" | "full";
};

export function SkeletonLine({ className = "", size = "full", style }: LineProps) {
  return <SkeletonBlock className={`skeleton-line skeleton-line--${size} ${className}`.trim()} style={style} />;
}

type PanelProps = {
  rows?: number;
  className?: string;
};

export function PanelSkeleton({ rows = 3, className = "" }: PanelProps) {
  const widths: LineProps["size"][] = ["lg", "full", "md", "full", "sm"];
  return (
    <div className={`panel-skeleton ${className}`.trim()} aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }, (_, i) => (
        <SkeletonLine key={i} size={widths[i % widths.length]} />
      ))}
    </div>
  );
}

type PageProps = {
  variant?: "default" | "dashboard" | "detail" | "gate";
};

export function PageSkeleton({ variant = "default" }: PageProps) {
  if (variant === "gate") {
    return (
      <div className="page-skeleton page-skeleton--gate" aria-busy="true" aria-label="Loading">
        <div className="panel page-skeleton-gate-card">
          <SkeletonLine size="lg" />
          <SkeletonLine size="full" />
          <SkeletonLine size="md" />
          <SkeletonBlock className="skeleton-btn" />
        </div>
      </div>
    );
  }

  if (variant === "dashboard") {
    return (
      <div className="page-skeleton page-skeleton--dashboard" aria-busy="true" aria-label="Loading dashboard">
        <div className="page-skeleton-intro">
          <SkeletonLine size="lg" />
          <SkeletonLine size="full" />
        </div>
        <SkeletonBlock className="skeleton-hero" />
        <div className="stats stats-compact page-skeleton-stats">
          {Array.from({ length: 4 }, (_, i) => (
            <SkeletonBlock key={i} className="skeleton-stat-card" />
          ))}
        </div>
        <div className="panel">
          <div className="panel-header">
            <SkeletonLine size="md" />
          </div>
          <div className="panel-body">
            <PanelSkeleton rows={4} />
          </div>
        </div>
      </div>
    );
  }

  if (variant === "detail") {
    return (
      <div className="page-skeleton page-skeleton--detail" aria-busy="true" aria-label="Loading control">
        <SkeletonLine size="sm" />
        <SkeletonLine size="lg" />
        <SkeletonLine size="full" />
        <div className="panel">
          <div className="panel-body panel-stack">
            <PanelSkeleton rows={5} />
            <SkeletonBlock className="skeleton-field" />
            <SkeletonBlock className="skeleton-field skeleton-field--tall" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-skeleton" aria-busy="true" aria-label="Loading">
      <div className="page-skeleton-intro">
        <SkeletonLine size="lg" />
        <SkeletonLine size="full" />
        <SkeletonLine size="md" />
      </div>
      <div className="panel-stack">
        <div className="panel">
          <div className="panel-body">
            <PanelSkeleton rows={4} />
          </div>
        </div>
        <div className="panel">
          <div className="panel-body">
            <PanelSkeleton rows={3} />
          </div>
        </div>
      </div>
    </div>
  );
}

type EmptyProps = {
  title: string;
  description?: string;
  children?: ReactNode;
  compact?: boolean;
};

export function EmptyState({ title, description, children, compact = false }: EmptyProps) {
  return (
    <div className={`empty-state${compact ? " empty-state--compact" : ""}`}>
      <p className="empty-state-title">{title}</p>
      {description && <p className="muted empty-state-description">{description}</p>}
      {children && <div className="empty-state-action">{children}</div>}
    </div>
  );
}
