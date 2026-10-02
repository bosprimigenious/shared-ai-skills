#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/public-release-privacy/scripts/scan_public_release.py" "${1:-$ROOT}"
