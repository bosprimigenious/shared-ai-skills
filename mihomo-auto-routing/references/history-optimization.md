# Recent-history optimization

Use this workflow only after the user explicitly authorizes local history aggregation and lightweight requests to the resulting domains.

## Privacy boundary

- Default window: 168 hours. Default ranking: top 10; never inspect more than 30 without a specific request.
- Query only visit timestamps and URLs needed to derive hostnames. Emit only normalized hostname and visit count.
- Never emit or retain full URLs, titles, queries, fragments, search terms, account paths, form data, cookies, or browser profile contents.
- Exclude localhost, IP literals, `.local` names, invalid hostnames, and single-visit noise by default.
- Keep redirected output in a restrictive temporary directory (`umask 077`). Remove it after the policy has been reviewed or if the user withdraws consent.
- Browser consent does not authorize configuration changes. Snapshot and validate before any separate authorized mutation.

`recent_domains.py` supports Safari, Chrome, Edge, Brave, Arc, and Firefox on macOS. It reads SQLite databases in read-only mode and reports per-browser permission/schema failures without exposing their paths. Do not copy protected databases or bypass TCC when access is denied.

## Measurement workflow

1. Aggregate recent domains locally:

   `python3 scripts/recent_domains.py --browser auto --hours 168 --limit 30 --min-visits 2`

2. Review the domain-only list. Exclude login, payment, health, internal, local-development, and other inappropriate health-check targets. Do not infer sensitive categories in the user-facing summary.
3. Ask before sending requests if the earlier consent covered history reading but not network probing.
4. Benchmark at most the top 10 approved domains against a broad physical-node source group:

   `scripts/rank_domains.sh DOMAINS.tsv SOURCE_GROUP [ACTIVE_CONFIG] [LIMIT]`

5. Create a dedicated group only when the site is frequent and routing differs materially. As a practical starting point, require at least three recent visits plus either a 20% latency improvement, a 200 ms improvement, or a demonstrated reliability/geo-routing need.
6. Route proven-fast domestic or local services directly. For international or route-sensitive services, create a site-specific `url-test` containing eligible physical nodes and a stable lightweight probe.
7. Keep the final general automatic group for the long tail. Do not create groups for every observed domain.

## Best-node semantics

The one-shot benchmark is evidence for group design, not a permanent winner. Configure recurring `url-test` with `lazy: true`, a 300–600 second interval, and about 30 ms tolerance so Mihomo continuously selects the best healthy candidate after the agent exits.

Preserve region, unlock, account-risk, and provider constraints. Lowest RTT alone is insufficient for services with geographic behavior.
