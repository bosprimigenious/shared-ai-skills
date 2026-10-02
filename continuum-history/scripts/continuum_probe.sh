#!/usr/bin/env bash
# Read-only probe. Does not open Cursor/Claude/Codex history or print message text.
set -euo pipefail

ROOT="${CONTINUUM_ROOT:-$HOME/Projects/ai-tools/continuum}"

echo "continuum_probe"
echo "root=$ROOT"

if [ ! -f "$ROOT/pyproject.toml" ] || [ ! -d "$ROOT/src/continuum_history" ]; then
  echo "status=missing_repo"
  echo "native=NOT_READY"
  exit 2
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "status=missing_uv"
  echo "native=NOT_READY"
  exit 2
fi

echo "uv=$(command -v uv)"
if ! uv run --directory "$ROOT" continuum --help >/dev/null; then
  echo "status=cli_failed"
  echo "native=NOT_READY"
  exit 2
fi
echo "cli=ok"

if [ -f "$ROOT/src/continuum_history/adapters/cursor_state_vscdb.py" ]; then
  echo "cursor_adapter=present"
else
  echo "cursor_adapter=absent"
fi

INDEX="${CONTINUUM_INDEX:-${CONTINUUM_DB:-}}"
if [ -n "$INDEX" ]; then
  if [ -f "$INDEX" ]; then
    echo "index=present"
  else
    echo "index=missing"
  fi
else
  echo "index=unspecified"
fi

echo "native=NOT_READY"
echo "note=live Cursor/Claude/Codex hosts unverified; do not scan home logs"
echo "status=ok"
