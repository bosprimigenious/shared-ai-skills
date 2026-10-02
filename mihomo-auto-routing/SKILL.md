---
name: mihomo-auto-routing
description: Diagnose and tune Mihomo or Clash Nyanpasu when a proxy/梯子 is slow, common sites should be discovered from recent browser history with explicit consent, per-site nodes should switch automatically, or routing must survive subscription updates. Use for privacy-preserving history aggregation, connectivity audits, site-specific url-test groups, DIRECT rules, controller reloads, and acceptance checks; do not use for unrelated VPN products without a Mihomo-compatible configuration.
---

# Mihomo Auto Routing

Make browsing reliably fast by combining site-aware routing with Mihomo's continuous `url-test`. The agent performs diagnosis and configuration; Mihomo keeps switching nodes after the agent exits.

## Choose the mode

- For “why is it slow?” or an audit, stay read-only and report measured DNS, connect, TLS, first-byte, direct-versus-proxy, current group, and node health.
- For “configure/fix/optimize/auto-switch,” snapshot first, render a candidate, validate it, then update both the persistent Nyanpasu merge and active config.
- Do not infer permission to edit configuration from a read-only question.

## Ask before reading browser history

When recent history would improve the result, ask one concise question before accessing it:

> 是否允许我仅在本机读取最近 7 天浏览历史，聚合为域名和访问次数，并对前 10 个普通网站域名发送轻量测速请求？不会读取或展示完整 URL、标题、搜索词、表单内容或账号路径。

Silence is not consent. If the user declines, cannot answer, or browser privacy controls deny access, continue with user-named sites plus the general automatic group. Never weaken OS privacy controls.

After consent, read [references/history-optimization.md](references/history-optimization.md). Use [scripts/recent_domains.py](scripts/recent_domains.py) to aggregate locally and [scripts/rank_domains.sh](scripts/rank_domains.sh) to compare current routing, direct access, and every eligible candidate in a source group. Keep intermediate domain lists private and temporary.

## Read guidance and policy

Read [references/nyanpasu-routing.md](references/nyanpasu-routing.md) before changing a Clash Nyanpasu installation or using browser history to derive rules.

Use [references/policy.example.yaml](references/policy.example.yaml) as the policy schema and safe starting point. Copy it outside this skill or supply a private overlay; never put machine identifiers, browsing history, credentials, or private domains in a public policy.

Use [scripts/mihomo_probe.sh](scripts/mihomo_probe.sh) for sanitized status, direct/proxy comparison, and group-wide delay tests. It never prints the controller secret or subscription URL.

Use [scripts/snapshot_nyanpasu.sh](scripts/snapshot_nyanpasu.sh) immediately before an authorized configuration change. Use `scripts/policy_tool.py render` to produce candidate active/merge files outside the live directory; never point its outputs at the live files. The executable Python script declares and locks its PyYAML dependency through `uv`.

Use `scripts/policy_tool.py validate` on both candidates and installed files. It rejects missing groups, wrong probe settings, nested/metadata candidates, rule-order drift, missing persistence entries, secrets in the merge, and YAML aliases. If `uv` is missing, report the dependency and stop before mutation; do not install software without authorization.

## Routing design

Prefer this hierarchy:

1. Explicit `DIRECT` rules for private networks and sites proven faster and reliable by direct access.
2. Dedicated `url-test` groups for high-frequency or route-sensitive services. Probe the actual service or a stable lightweight endpoint on the same service.
3. A general `url-test` group for all unmatched international traffic.
4. A final `MATCH` rule pointing to the general automatic selector.

Do not create one group per browser-history row. Aggregate to registrable domains and create dedicated groups only when routing differs materially; the final automatic selector covers the long tail.

For a dedicated group:

- Compare every eligible physical node against that site's probe.
- Remove metadata proxies, nested selectors, and nodes that time out consistently.
- Use `lazy: true`, an interval around 300–600 seconds, and a tolerance around 30 ms unless measurements justify otherwise.
- Include the site's asset/CDN domains when the page shell and media use different hosts.
- Preserve region/unlock constraints for ChatGPT, streaming, or other geo-sensitive services; lowest RTT alone is not sufficient.
- Select through recurring `url-test`, not by permanently pinning the node that wins one sample.

## Safe mutation sequence

1. Resolve exact config, merge profile, controller, and Mihomo binary paths from the running process and `profiles.yaml`; do not guess IDs.
2. Run `snapshot_nyanpasu.sh` to create a timestamped tar snapshot containing the active config, `profiles.yaml`, profile sources, and guard overrides. Keep its restrictive permissions and print the archive member list and checksum.
3. Run `policy_tool.py render` with the active config, resolved merge file, and a policy YAML; write both candidates to `work/` or another temporary directory. Show its group/rule summary as the dry-run.
4. Run `mihomo -t` against the candidate. Do not install a failing candidate.
5. Update the merge profile referenced by `profiles.chain` so subscription refreshes retain the routing. Keep secrets and subscription URLs unchanged.
6. Install the validated candidate and hot-reload through the authenticated local controller.
7. Force group delay tests, then verify page and representative CDN requests end to end.
8. If a post-install hard gate fails, restore the snapshot and reload the restored config.

After reload, when the supplied policy defines `default_selector`, set its named selector to the configured choice through the controller. A valid config with that selector still stuck on a fixed node is not complete.

Avoid YAML aliases in persisted merge files unless the installed Nyanpasu parser has been explicitly verified to accept them.

## Acceptance gate

Report READY only when all applicable checks pass:

- installed config passes `mihomo -t`;
- `policy_tool.py validate` passes against the installed active and merge files;
- controller reload returns HTTP 204;
- runtime group types and selected nodes match the design;
- runtime rule order routes sampled domains to the intended policy;
- actual page requests succeed, including representative CDN resources where relevant;
- the merge file parses without placeholders or unexpected YAML aliases and remains referenced by `profiles.chain`.

State separately whether a real subscription refresh was tested. Never claim refresh persistence solely because the merge file exists.
