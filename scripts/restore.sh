#!/usr/bin/env bash
# Khestra data restore — copy a backup back into the app data dirs.
#
# Usage:
#   ./scripts/restore.sh backups/khestra-backup-20260807-101500     # restore in place
#   TARGET=/scratch/restore ./scripts/restore.sh <backup>           # restore to scratch (drill)
#
# Restoring in place OVERWRITES live data — run the drill to a scratch
# TARGET first and verify the app boots against it before any real restore.
# POSIX-compatible (macOS bash 3.2).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:?usage: restore.sh <backup-dir> [TARGET=]}"
TARGET="${TARGET:-}"

if [ ! -d "$SRC" ]; then
  echo "Backup dir not found: $SRC" >&2
  exit 1
fi

# Map backup subdir names → live app data dirs (case-based, POSIX-safe).
resolve_dest() {
  case "$1" in
    data|cmmc_data)            echo "$ROOT/data";;
    soc2_data)                 echo "$ROOT/apps/soc2/soc2_data";;
    aigov_data|aigovernance_data) echo "$ROOT/apps/aigovernance/data";;
    iso27001_data|iso_data)    echo "$ROOT/apps/iso27001/data";;
    core_data|core)            echo "$ROOT/apps/core/data";;
    *)                         echo "";;
  esac
}

for name in "$SRC"/*/; do
  base="$(basename "$name")"
  dest="$(resolve_dest "$base")"
  if [ -z "$dest" ]; then
    echo "SKIP (no live dir mapped): $base"
    continue
  fi
  if [ -n "$TARGET" ]; then
    out="$TARGET/$base"
    mkdir -p "$out"
  else
    out="$dest"
  fi
  echo "restore $base → $out"
  rsync -a --delete "$name" "$out"
done

if [ -n "$TARGET" ]; then
  echo ""
  echo "Drill restore complete: $TARGET"
  echo "Verify: sqlite3 integrity check + app boot against $TARGET before any real restore."
else
  echo ""
  echo "Restore complete. Restart the services (docker compose restart)."
fi
