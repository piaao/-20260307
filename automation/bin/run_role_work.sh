#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <role-id>"
  exit 1
fi

ROLE_ID="$1"
ROOT="/home/admin/.openclaw/workspace"
LOCK_DIR="$ROOT/automation/state/locks"
LOCK_FILE="$LOCK_DIR/${ROLE_ID}.work.lock"

mkdir -p "$LOCK_DIR"
cd "$ROOT"

/usr/bin/flock -n "$LOCK_FILE" /usr/bin/python3 automation/bin/work_runner.py --role "$ROLE_ID"
