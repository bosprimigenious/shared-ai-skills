#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' 'Usage: rank_domains.sh DOMAINS.tsv SOURCE_GROUP [ACTIVE_CONFIG] [LIMIT]'
}

input_file="${1:-}"
source_group="${2:-}"
default_config="$HOME/Library/Application Support/Clash Nyanpasu/config/clash-config.yaml"
config_path="${3:-$default_config}"
limit="${4:-10}"

[[ -n "$input_file" && -n "$source_group" ]] || { usage; exit 2; }
[[ -r "$input_file" ]] || { echo "domain list not readable: $input_file" >&2; exit 1; }
[[ "$limit" =~ ^[0-9]+$ && "$limit" -ge 1 && "$limit" -le 30 ]] || { echo 'LIMIT must be 1..30' >&2; exit 2; }

for binary in curl jq sed awk sort head; do
  command -v "$binary" >/dev/null || { echo "missing binary: $binary" >&2; exit 1; }
done
[[ -r "$config_path" ]] || { echo "config not readable: $config_path" >&2; exit 1; }

controller=$(sed -n 's/^external-controller:[[:space:]]*//p' "$config_path" | head -1 | tr -d "'\"")
controller_secret=$(sed -n 's/^secret:[[:space:]]*//p' "$config_path" | head -1 | tr -d "'\"")
[[ -n "$controller" ]] || { echo 'external-controller not found' >&2; exit 1; }

auth_args=()
[[ -n "$controller_secret" ]] && auth_args=(-H "Authorization: Bearer $controller_secret")
encoded_group=$(printf '%s' "$source_group" | jq -sRr @uri)

printf 'domain\tvisits\tcurrent_code\tcurrent_s\tdirect_code\tdirect_s\tbest_node\tbest_ms\n'
while IFS=$'\t' read -r domain visits; do
  [[ "$domain" == "domain" ]] && continue
  [[ "$domain" =~ ^[A-Za-z0-9.-]+$ && "$domain" == *.* ]] || continue
  target_url="https://$domain/"
  encoded_url=$(printf '%s' "$target_url" | jq -sRr @uri)

  if ! current=$(curl -L -sS -o /dev/null --connect-timeout 5 --max-time 15 \
    -w '%{http_code}\t%{time_total}' "$target_url" 2>/dev/null); then
    current=$'000\terror'
  fi
  if ! direct=$(curl --noproxy '*' -L -sS -o /dev/null --connect-timeout 5 --max-time 15 \
    -w '%{http_code}\t%{time_total}' "$target_url" 2>/dev/null); then
    direct=$'000\terror'
  fi
  delays=$(curl --noproxy '*' -sS --max-time 20 "${auth_args[@]}" \
    "http://$controller/group/$encoded_group/delay?timeout=10000&url=$encoded_url" 2>/dev/null || printf '{}')
  best=$(printf '%s' "$delays" | jq -r '
    [to_entries[] | select(.value | type == "number")]
    | sort_by(.value) | first
    | if . then [.key, (.value | tostring)] | @tsv else "unavailable\tunavailable" end
  ' 2>/dev/null || printf 'unavailable\tunavailable')
  printf '%s\t%s\t%s\t%s\t%s\n' "$domain" "$visits" "$current" "$direct" "$best"
done < <(awk -F '\t' 'NR > 1 && $2 ~ /^[0-9]+$/ { print $1 "\t" $2 }' "$input_file" | sort -t $'\t' -k2,2nr | head -n "$limit")
