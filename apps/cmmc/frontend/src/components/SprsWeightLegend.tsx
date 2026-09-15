import SprsWeightBadge from "./SprsWeightBadge";

export default function SprsWeightLegend() {
  return (
    <div className="sprs-weight-legend">
      <span className="sprs-weight-legend-title">SPRS weights</span>
      <SprsWeightBadge label="5 PT" tier="critical" />
      <span className="sprs-weight-legend-note">Critical</span>
      <SprsWeightBadge label="3 PT" tier="standard" />
      <span className="sprs-weight-legend-note">Standard</span>
      <SprsWeightBadge label="1 PT" tier="low" />
      <span className="sprs-weight-legend-note">Low</span>
      <SprsWeightBadge label="5/3 PT" tier="variable" />
      <span className="sprs-weight-legend-note">Variable (MFA / FIPS)</span>
    </div>
  );
}
