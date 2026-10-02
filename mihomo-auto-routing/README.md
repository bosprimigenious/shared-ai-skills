# mihomo-auto-routing

A reusable Codex-compatible Skill for diagnosing slow Mihomo or Clash Nyanpasu connections and maintaining automatic per-site node selection.

## Install

Clone this repository into your agent's skills directory. For Codex:

```bash
git clone https://github.com/bosprimigenious/mihomo-auto-routing.git ~/.codex/skills/mihomo-auto-routing
```

Start a new session, then ask “优化一下梯子” or invoke `$mihomo-auto-routing`.

The Skill asks before reading recent browser history. With consent, it aggregates only local domain names and visit counts, benchmarks the most common approved sites, and configures recurring Mihomo `url-test` groups. It does not output full URLs, page titles, searches, cookies, or credentials.

Requirements: macOS, a Mihomo-compatible configuration, Python 3.8+, `uv`, Bash, `curl`, and `jq`. The policy tool declares and locks `PyYAML==6.0.3`; `uv` creates an isolated environment automatically on first use.

Licensed under MIT.
