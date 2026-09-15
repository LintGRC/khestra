# Shared evidence collection

Framework-agnostic collector layer used by Khestra apps.

## Contents (`collectors/`)

- `connectors/` — Entra, AWS, GitHub, Intune
- `engine.py` — `run_collector`, `recent_runs` (no control attach)
- `registry.py`, `credentials_store.py`, `drift.py`, `monitor_store.py`
- `scheduler_config.py`, `dev_scheduler.py`, `webhook_store.py`
- `attach_registry.py` — apps register `controls_for_check` at import time

## CMMC app wiring

`apps/cmmc/core/cmmc_collectors/` imports `cmmc_collectors` on startup, which calls:

```python
register_control_mapper(controls_for_check)  # CHECK_TO_CONTROLS in mapping.py
```

Attach to workspace controls: `cmmc_collectors.attach.run_and_attach`.

## SOC 2 (future)

Add `apps/soc2/core/soc2_collectors/mapping.py` with TSC criteria mapping and reuse the same evidence package.
