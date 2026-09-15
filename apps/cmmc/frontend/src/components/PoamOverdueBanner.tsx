import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../api";

function focusLink(controlId: string) {
  return `/controls?focus=${encodeURIComponent(controlId)}`;
}

export default function PoamOverdueBanner() {
  const [alerts, setAlerts] = useState<{ control_id: string; message: string }[]>([]);

  useEffect(() => {
    api.alerts().then((data) => setAlerts(data.poam_overdue || [])).catch(console.error);
  }, []);

  if (alerts.length === 0) return null;

  return (
    <div className="banner warning poam-overdue-banner">
      <strong>{alerts.length} overdue POA&amp;M item(s):</strong>{" "}
      {alerts.slice(0, 5).map((a, i) => (
        <span key={a.control_id}>
          {i > 0 && ", "}
          <Link to={focusLink(a.control_id)}>{a.control_id}</Link>
        </span>
      ))}
      {alerts.length > 5 && <span className="muted"> …and {alerts.length - 5} more</span>}
    </div>
  );
}
