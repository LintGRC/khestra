#!/usr/bin/env bash
# Khestra production smoke test — one-command pass/fail for ops.
#
# Usage (on the staging/prod host, or anywhere reachable):
#   DOMAIN=app.khestra.com \
#   ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='<strong>' \
#   SCHEDULER_TOKEN='<token>' ALLOWED_ORIGIN=https://app.khestra.com \
#   ./scripts/smoke.sh
#
# Asserts: all service health endpoints, UI over HTTPS, demo endpoints 403,
# CORS honors the allowlist, auth login works, collector surface + scheduler
# heartbeat + scheduled run, and an export downloads. Exits nonzero on any
# failure and prints a summary.
set -euo pipefail

DOMAIN="${DOMAIN:?DOMAIN required (e.g. app.khestra.com)}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:?ADMIN_PASSWORD required}"
SCHEDULER_TOKEN="${SCHEDULER_TOKEN:-}"
ALLOWED_ORIGIN="${ALLOWED_ORIGIN:-https://$DOMAIN}"
SCHEME="${SCHEME:-https}"
BASE="$SCHEME://$DOMAIN"

PASS=0
FAIL=0

ok()   { PASS=$((PASS + 1)); echo "PASS  $1"; }
bad()  { FAIL=$((FAIL + 1)); echo "FAIL  $1"; }

check_code() { # name expected actual
  if [ "$3" = "$2" ]; then ok "$1 ($3)"; else bad "$1 (expected $2, got $3)"; fi
}

echo "== Khestra smoke — $BASE"
echo ""

# 1. Health endpoints (framework prefixes + global core).
check_code "health /api/health (cmmc)" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "$BASE/api/health")"
check_code "health /api/soc2/health"    200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "$BASE/api/soc2/health")"
check_code "health /api/ai-governance/health" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "$BASE/api/ai-governance/health")"
check_code "health /api/iso27001/health" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "$BASE/api/iso27001/health")"
check_code "health /api/core/health (global)" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "$BASE/api/core/health")"

# 2. UI over HTTPS.
ui_code="$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "$BASE/")"
check_code "UI loads over HTTPS" 200 "$ui_code"

# 3. Auth login (local mode behind trusted network).
TOKEN="$(curl -s --max-time 10 -X POST "$BASE/api/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("token",""))' 2>/dev/null || true)"
if [ -n "$TOKEN" ]; then ok "auth login"; else bad "auth login (no token — wrong credentials or auth misconfigured)"; fi

AUTH=(-H "Authorization: Bearer $TOKEN")

# 4. Demo endpoints must be disabled in production (403, auth'd).
check_code "demo load disabled" 403 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' -X POST "${AUTH[@]}" "$BASE/api/demo/load")"

# 5. CORS honors the allowlist.
cors="$(curl -s --max-time 10 -D - -o /dev/null -H "Origin: $ALLOWED_ORIGIN" "$BASE/api/health" | tr -d '\r' | grep -i '^access-control-allow-origin:' | head -1 | cut -d' ' -f2 || true)"
if [ "$cors" = "$ALLOWED_ORIGIN" ]; then ok "CORS allowlist ($cors)"; else bad "CORS allowlist (got '$cors', want $ALLOWED_ORIGIN)"; fi

# 6. Collector surface + scheduler heartbeat (auth'd).
check_code "collectors list (auth'd)" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "${AUTH[@]}" "$BASE/api/collectors")"
check_code "scheduler heartbeat (auth'd)" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "${AUTH[@]}" "$BASE/api/collectors/monitoring/scheduler-status")"

# 7. Scheduled run with the scheduler token (unauth'd path is token-gated).
if [ -n "$SCHEDULER_TOKEN" ]; then
  run_code="$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' -X POST \
    -H "Authorization: Bearer $SCHEDULER_TOKEN" -H 'Content-Type: application/json' \
    -d '{}' "$BASE/api/collectors/monitoring/run-due")"
  check_code "scheduled run-due (scheduler token)" 200 "$run_code"
else
  echo "SKIP  scheduled run-due (SCHEDULER_TOKEN not set)"
fi

# 8. Export downloads (auth'd).
check_code "POA&M export (auth'd)" 200 "$(curl -s --max-time 10 -o /dev/null -w '%{http_code}' "${AUTH[@]}" "$BASE/api/export/poam")"

echo ""
echo "== Summary: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
