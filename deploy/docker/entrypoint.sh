#!/bin/sh
# Khestra container entrypoint — privilege-drop pattern for persistent volumes.
#
# Runs as root to fix volume ownership (bind-mounts belong to the host UID),
# hardens the connector-credential directories to 0700, then drops to the
# non-root `appuser` for the actual service. Volume-permission trap avoided:
# a non-root process cannot chown files it does not own, so chown happens
# BEFORE the privilege drop.
set -e

DATA_DIR="${DATA_DIR:-/data}"
SHARED_AUTH_DIR="${SHARED_AUTH_DIR:-/shared/auth}"

# 1. Fix ownership of the mounted data dirs (idempotent).
for d in "$DATA_DIR" "$SHARED_AUTH_DIR"; do
  if [ -d "$d" ]; then
    chown -R appuser:appuser "$d" 2>/dev/null || true
  fi
done

# 2. Connector credentials are a secrets store — service user only.
#    (collector state lives under collectors/; both get 0700.)
for c in \
  "$DATA_DIR/connectors" \
  "$DATA_DIR/collectors" \
  "$SHARED_AUTH_DIR/connectors" \
  "$SHARED_AUTH_DIR/collectors"; do
  mkdir -p "$c" 2>/dev/null || true
  chmod 0700 "$c" 2>/dev/null || true
  chown appuser:appuser "$c" 2>/dev/null || true
done

# 3. Run the service as the unprivileged user.
exec gosu appuser "$@"
