#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage:' \
    '  mihomo_probe.sh status [config]' \
    '  mihomo_probe.sh compare URL [config]' \
    '  mihomo_probe.sh group GROUP URL [config]'
}

mode="${1:-}"
if [[ -z "$mode" ]]; then
  usage
  exit 2
fi

default_config="$HOME/Library/Application Support/Clash Nyanpasu/config/clash-config.yaml"
case "$mode" in
  status) config_path="${2:-$default_config}" ;;
  compare) target_url="${2:-}"; config_path="${3:-$default_config}" ;;
  group) group_name="${2:-}"; target_url="${3:-}"; config_path="${4:-$default_config}" ;;
  *) usage; exit 2 ;;
esac

for binary in curl jq sed; do
  command -v "$binary" >/dev/null || { echo "missing binary: $binary" >&2; exit 1; }
done
[[ -r "$config_path" ]] || { echo "config not readable: $config_path" >&2; exit 1; }

controller=$(sed -n 's/^external-controller:[[:space:]]*//p' "$config_path" | head -1 | tr -d "'\"")
controller_secret=$(sed -n 's/^secret:[[:space:]]*//p' "$config_path" | head -1 | tr -d "'\"")
mixed_port=$(sed -n 's/^mixed-port:[[:space:]]*//p' "$config_path" | head -1)
[[ -n "$controller" ]] || { echo 'external-controller not found' >&2; exit 1; }

auth_args=()
[[ -n "$controller_secret" ]] && auth_args=(-H "Authorization: Bearer $controller_secret")

case "$mode" in
  status)
    printf 'config=%s\ncontroller=%s\nmixed_port=%s\n' "$config_path" "$controller" "${mixed_port:-unknown}"
    curl --noproxy '*' -sS --max-time 5 "${auth_args[@]}" "http://$controller/proxies" |
      jq -r '.proxies | to_entries[] | select(.value.type=="Selector" or .value.type=="URLTest") | [.key,.value.type,.value.now] | @tsv' |
      sort
    ;;
  compare)
    [[ -n "$target_url" ]] || { usage; exit 2; }
    curl -L -sS -o /dev/null --connect-timeout 5 --max-time 15 \
      -w 'current code=%{http_code} dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s first=%{time_starttransfer}s total=%{time_total}s\n' "$target_url" || true
    curl --noproxy '*' -L -sS -o /dev/null --connect-timeout 5 --max-time 15 \
      -w 'direct  code=%{http_code} dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s first=%{time_starttransfer}s total=%{time_total}s\n' "$target_url" || true
    ;;
  group)
    [[ -n "$group_name" && -n "$target_url" ]] || { usage; exit 2; }
    encoded_group=$(printf '%s' "$group_name" | jq -sRr @uri)
    encoded_url=$(printf '%s' "$target_url" | jq -sRr @uri)
    curl --noproxy '*' -sS --max-time 20 "${auth_args[@]}" \
      "http://$controller/group/$encoded_group/delay?timeout=10000&url=$encoded_url" |
      jq -r 'if .message then "ERROR\t"+.message else to_entries | sort_by(.value)[] | [.key,(.value|tostring)+"ms"] | @tsv end'
    printf 'selected\t'
    curl --noproxy '*' -sS --max-time 5 "${auth_args[@]}" \
      "http://$controller/proxies/$encoded_group" | jq -r '.now'
    ;;
esac
