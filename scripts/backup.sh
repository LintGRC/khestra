#!/usr/bin/env bash
# Khestra data backup — rsync of every app data dir to a timestamped backup.
#
# Usage:
#   ./scripts/backup.sh                     # → $BACKUP_DIR/khestra-backup-YYYYMMDD-HHMMSS/
#   BACKUP_DIR=/mnt/backups ./scripts/backup.sh
#   KEEP=14 ./scripts/backup.sh             # rotate: keep N backups (default 7)
#
# Includes auth.db + auth_secret (needed together — tokens are signed by the
# secret) and connector credentials (encrypted at rest). Treat the backup
# location like a secrets store. Excludes caches and temp files only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT/backups}"
KEEP="${KEEP:-7}"

DATA_DIRS=(
  "$ROOT/data|cmmc_data"
  "$ROOT/apps/soc2/soc2_data|soc2_data"
  "$ROOT/apps/aigovernance/data|aigov_data"
  "$ROOT/apps/iso27001/data|iso27001_data"
  "$ROOT/apps/core/data|core_data"
)

STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$BACKUP_DIR/khestra-backup-$STAMP"
mkdir -p "$DEST"

EXCLUDES=(--exclude '__pycache__' --exclude '*.pyc' --exclude '*.tmp'
          --exclude '.DS_Store' --exclude 'wip-*' --exclude '*.log')

for entry in "${DATA_DIRS[@]}"; do
  d="${entry%%|*}"
  name="${entry##*|}"
  if [ -d "$d" ]; then
    echo "backing up $d → $DEST/$name"
    rsync -a "${EXCLUDES[@]}" "$d/" "$DEST/$name/"
  else
    echo "SKIP (missing): $d"
  fi
done

# Rotate old backups.
ls -1dt "$BACKUP_DIR"/khestra-backup-* 2>/dev/null | tail -n +$((KEEP + 1)) | while read -r old; do
  echo "rotating out: $old"
  rm -rf "$old"
done

MANIFEST="$DEST/MANIFEST.txt"
{
  echo "backed_up_at=$STAMP"
  echo "host=$(hostname)"
  echo "dirs=${DATA_DIRS[*]}"
  echo "restore=./scripts/restore.sh $DEST"
} > "$MANIFEST"

echo ""
echo "Backup complete: $DEST"
echo "Next: verify with a restore drill — ./scripts/restore.sh $DEST (to a scratch copy first)."
