import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type PriorityQueueItem, type PriorityQueueResult } from "../api";

type Tier = "risk" | "urgent" | "fast" | "blocked";

const TIER_CONFIG: Record<Tier, { label: string; color: string; icon: string }> = {
  risk: { label: "Highest Risk", color: "var(--danger)", icon: "!" },
  urgent: { label: "Due This Week", color: "var(--warning)", icon: "!" },
  fast: { label: "Fast Wins", color: "var(--success)", icon: "+" },
  blocked: { label: "Blocked", color: "var(--muted)", icon: "!" },
};

const TIER_ORDER: Tier[] = ["risk", "urgent", "fast", "blocked"];

export default function PriorityQueue() {
  const [data, setData] = useState<PriorityQueueResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTier, setActiveTier] = useState<Tier | "all">("all");

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.priorityQueue(50);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load priority queue");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="p-4 muted">Loading priority queue…</div>;
  if (error) return <div className="p-4 error">{error}</div>;
  if (!data) return null;

  const filtered = activeTier === "all"
    ? data.items
    : data.items.filter((i) => i.tier === activeTier);

  return (
    <div className="p-4" style={{ maxWidth: 1000, margin: "0 auto" }}>
      <h1 className="page-title">Priority Queue</h1>
      <p className="muted" style={{ margin: "4px 0 20px" }}>
        Controls sorted by impact. Work from top to bottom.
      </p>

      {/* Tier summary */}
      <div className="row" style={{ gap: 10, marginBottom: 20, flexWrap: "wrap" }}>
        <button
          className={`btn btn-sm ${activeTier === "all" ? "btn-primary" : ""}`}
          onClick={() => setActiveTier("all")}
        >
          All ({data.total})
        </button>
        {TIER_ORDER.map((tier) => (
          <button
            key={tier}
            className={`btn btn-sm ${activeTier === tier ? "btn-primary" : ""}`}
            onClick={() => setActiveTier(tier)}
            style={{ borderLeft: `3px solid ${TIER_CONFIG[tier].color}` }}
          >
            {TIER_CONFIG[tier].label} ({data.tier_counts[tier]})
          </button>
        ))}
      </div>

      {/* Items */}
      {filtered.length === 0 ? (
        <div className="card p-4 centered">
          <h3>No controls in this tier</h3>
          <p className="muted">Nothing to work on here.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {filtered.map((item, idx) => (
            <PriorityRow key={item.control_id} item={item} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
}

function PriorityRow({ item, index }: { item: PriorityQueueItem; index: number }) {
  const cfg = TIER_CONFIG[item.tier as Tier] || { label: "Normal", color: "var(--muted)", icon: "" };
  return (
    <div className="card" style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px" }}>
      <span
        className="badge"
        style={{
          background: cfg.color,
          color: "#fff",
          minWidth: 28,
          textAlign: "center",
          fontWeight: 600,
        }}
      >
        {index + 1}
      </span>
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Link
            to={`/criteria/${item.control_id}`}
            style={{ fontWeight: 500, textDecoration: "none" }}
          >
            {item.control_id}
          </Link>
          <span style={{ fontSize: 13 }}>{item.name}</span>
        </div>
        <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4, display: "flex", gap: 12, flexWrap: "wrap" }}>
          <span>{item.category}</span>
          <span style={{ color: item.status === "NOT STARTED" ? "var(--warning)" : "inherit" }}>
            {item.status}
          </span>
          {item.owner && <span>Owner: {item.owner}</span>}
          {item.target_date && <span>Due: {item.target_date}</span>}
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 2 }}>
        {item.reasons.map((r, i) => (
          <span key={i} style={{ fontSize: 11, color: cfg.color, fontWeight: 500 }}>
            {cfg.icon} {r}
          </span>
        ))}
      </div>
    </div>
  );
}
