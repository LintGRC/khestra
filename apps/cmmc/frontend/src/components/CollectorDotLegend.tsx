export default function CollectorDotLegend() {
  return (
    <div className="collector-dot-legend">
      <span className="collector-dot-legend-title">Automated checks</span>
      <span className="collector-dot collector-dot--pass" />
      <span className="collector-dot-legend-note">All passing</span>
      <span className="collector-dot collector-dot--fail" />
      <span className="collector-dot-legend-note">Some failing</span>
      <span className="collector-dot collector-dot--error" />
      <span className="collector-dot-legend-note">Collector error</span>
      <span className="collector-dot collector-dot--idle" />
      <span className="collector-dot-legend-note">No data yet</span>
    </div>
  );
}
