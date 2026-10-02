#!/usr/bin/env bash
# Aggregate gate for framework-map fixtures. Fail closed.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
map="$root/scripts/check_framework_map.py"
note="$root/scripts/check_note.py"
ok=0
"$map" "$root/references/eval/pass.md" || ok=1
"$map" --expect-fail "$root/references/eval/fail-details.md" || ok=1
"$map" --expect-fail "$root/references/eval/fail-too-deep.md" || ok=1
"$note" "$root/references/eval/pass.md" || ok=1
"$note" --expect-fail "$root/references/eval/fail-no-cues.md" || ok=1
"$note" --expect-fail "$root/references/eval/fail-meta.md" || ok=1
"$note" --expect-fail "$root/references/eval/fail-details.md" || ok=1
if [ "$ok" -ne 0 ]; then
  echo "NOT READY: note eval"
  exit 1
fi
echo "READY: framework-map and note fixtures"
