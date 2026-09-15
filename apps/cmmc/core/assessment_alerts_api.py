"""POA&M overdue alerts — no Streamlit."""

from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from assessment_helpers import generate_poam_entries


def poam_overdue_alerts(answers: Dict[str, Any], scoped_controls: List[str]) -> List[Dict[str, str]]:
    poam_df = generate_poam_entries(answers, scoped_controls)
    if poam_df.empty:
        return []
    overdue = poam_df[pd.to_datetime(poam_df["Target Date"], errors="coerce") < pd.Timestamp.now()]
    alerts = []
    for _, row in overdue.iterrows():
        alerts.append(
            {
                "control_id": row["Control ID"],
                "target_date": str(row.get("Target Date", "")),
                "status": row.get("Current Status", ""),
                "message": f"{row['Control ID']} past target date ({row.get('Target Date', '')})",
            }
        )
    return alerts
