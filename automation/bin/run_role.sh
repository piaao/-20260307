#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <role-id>"
  exit 1
fi

ROLE_ID="$1"
ROOT="/home/admin/.openclaw/workspace"

cd "$ROOT"
/usr/bin/python3 automation/bin/role_runner.py --role "$ROLE_ID"
