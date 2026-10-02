#!/usr/bin/env bash
# Synthetic skill path: probe, import, search, read. Does not open live vendor logs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${CONTINUUM_ROOT:-$HOME/Projects/ai-tools/continuum}"
SNAP="$ROOT/examples/synthetic.snapshot.json"

bash "$SCRIPT_DIR/continuum_probe.sh"

if [ ! -f "$SNAP" ]; then
  echo "status=missing_fixture"
  exit 2
fi

TMP="$(mktemp -d "${TMPDIR:-/tmp}/continuum-skill-check.XXXXXX")"
INDEX="$TMP/index.db"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

sha() {
  python3 -c "import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())" "$1"
}

cli() {
  uv run --directory "$ROOT" continuum --db "$INDEX" --format json "$@"
}

before="$(sha "$SNAP")"
imported="$(cli import "$SNAP")"
python3 -c "import json,sys; d=json.loads(sys.argv[1]); assert d.get('event_count')==3, d; assert d.get('changed') is True" "$imported"

listed="$(cli sources)"
python3 -c "import json,sys; items=json.loads(sys.argv[1]).get('items') or []; assert items, sys.argv[1]" "$listed"
hits="$(cli search '数据库锁')"
session_id="$(python3 -c "import json,sys; items=json.loads(sys.argv[1]).get('items') or []; assert items, sys.argv[1]; print(items[0]['session_id'])" "$hits")"
implicit="$(uv run --directory "$ROOT" continuum --db "$INDEX" --format json 数据库锁)"
python3 -c "import json,sys; items=json.loads(sys.argv[1]).get('items') or []; assert items, sys.argv[1]" "$implicit"

events="$(cli read "$session_id" --limit 20)"
python3 -c "import json,sys; d=json.loads(sys.argv[1]); items=d.get('items') or []; assert len(items)==3, d; assert d.get('next_cursor') is None, d" "$events"

again="$(cli import "$SNAP")"
python3 -c "import json,sys; d=json.loads(sys.argv[1]); assert d.get('changed') is False, d" "$again"
after="$(sha "$SNAP")"
if [ "$before" != "$after" ]; then
  echo "status=source_mutated"
  exit 2
fi

echo "session_id=$session_id"
echo "status=ok"
echo "PASS: continuum-history skill synthetic path"
