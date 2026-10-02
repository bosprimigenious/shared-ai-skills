#!/usr/bin/env bash
set -euo pipefail

config_dir="${1:-$HOME/Library/Application Support/Clash Nyanpasu/config}"
[[ -d "$config_dir" ]] || { echo "config directory not found: $config_dir" >&2; exit 1; }

for binary in tar shasum date; do
  command -v "$binary" >/dev/null || { echo "missing binary: $binary" >&2; exit 1; }
done

required=(clash-config.yaml profiles.yaml profiles)
for target in "${required[@]}"; do
  [[ -e "$config_dir/$target" ]] || { echo "required target missing: $config_dir/$target" >&2; exit 1; }
done

targets=(clash-config.yaml profiles.yaml profiles)
[[ -f "$config_dir/clash-guard-overrides.yaml" ]] && targets+=(clash-guard-overrides.yaml)

backup_dir="$config_dir/codex-backups"
timestamp=$(date '+%Y%m%d-%H%M%S')
backup_file="$backup_dir/mihomo-auto-routing.$timestamp.$$.tar.gz"
umask 077
mkdir -p "$backup_dir"
tar -czf "$backup_file" -C "$config_dir" "${targets[@]}"
chmod 600 "$backup_file"

printf 'backup=%s\n' "$backup_file"
tar -tzf "$backup_file"
shasum -a 256 "$backup_file"
