# Clash Nyanpasu routing notes

## Local discovery

The common macOS installation uses these paths, but always resolve them from the running process and profile index before editing:

- active config: `~/Library/Application Support/Clash Nyanpasu/config/clash-config.yaml`
- profile index: `~/Library/Application Support/Clash Nyanpasu/config/profiles.yaml`
- profile files: `~/Library/Application Support/Clash Nyanpasu/config/profiles/`
- data directory: `~/Library/Application Support/Clash Nyanpasu/data`

The active merge profile is named in `profiles.yaml` under `chain`. Update that source and the active generated config; a controller-only selector change is not durable.

Read the controller `secret` without echoing it. Pass it only in the localhost `Authorization: Bearer` header. Redact proxy credentials, UUIDs, tokens, subscription URLs, page paths, queries, and browser-history details from output.

## Policy design baseline

Preserve and extend existing groups rather than replacing the subscription's stack.

Use one policy YAML as the structured source for direct rules, service probes, persistence mode, intervals, tolerance, and the desired default selector. Change that file first, then render candidates; do not maintain a second hard-coded copy in shell commands.

Representative service probes:

- GitHub: `https://github.com/`
- ChatGPT: `https://chat.openai.com/cdn-cgi/trace`
- Streaming: prefer a small stable endpoint on the target service; a successful connectivity probe does not prove regional catalog unlock
- Telegram: `https://telegram.org/`
- TikTok: `https://www.tiktok.com/`
- X/Twitter: `https://x.com/`
- WhatsApp: `https://web.whatsapp.com/`
- Copilot: `https://copilot.microsoft.com/`
- Google/general: `https://www.gstatic.com/generate_204`
- Steam: `https://store.steampowered.com/`

Re-measure before changing candidates. Node quality changes over time; do not preserve a historical winner as a permanent truth.

## Browser-history-derived rules

Only inspect browser history after explicit consent for the current optimization task. Follow [history-optimization.md](history-optimization.md) for the bounded collection and measurement workflow.

Safari may protect `History.db` through macOS privacy controls. Do not bypass that protection or request broader access merely for optimization. Use the History UI for visible evidence, optimize common observed domains, and rely on the general automatic selector for the long tail. Make this limitation explicit.

Favor explicit direct routing for private IP ranges, local services, and Chinese/work domains only after direct connectivity is verified. Keep login, payment, API-key, and internal pages out of health-check URLs.

## Practical checks

For each target, compare current routing and forced direct access with `curl` timing fields. A connection starting is not enough: capture HTTP status and total time, and distinguish application HTTP errors from network timeouts.

Use the controller group delay endpoint to force all candidates:

`GET /group/{encoded-group}/delay?timeout=10000&url={encoded-url}`

After probing, read `/proxies` again because a `URLTest` selection can change. Verify `/rules` ordering for representative domains. For a media site, request both the page and one asset URL from its actual HTML.

If a check script has quoting, encoding, parser, or timeout bugs, report that as a tool failure and rerun it; do not blame the proxy configuration.
