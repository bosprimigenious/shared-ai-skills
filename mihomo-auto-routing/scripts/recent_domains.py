#!/usr/bin/env python3
"""Aggregate recent browser history into domain/count pairs without emitting URLs."""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import ipaddress
import json
import os
from pathlib import Path
import sqlite3
import sys
from urllib.parse import quote, urlsplit


MAC_SOURCES = {
    "safari": ("safari", ["~/Library/Safari/History.db"]),
    "chrome": ("chromium", ["~/Library/Application Support/Google/Chrome/*/History"]),
    "edge": ("chromium", ["~/Library/Application Support/Microsoft Edge/*/History"]),
    "brave": ("chromium", ["~/Library/Application Support/BraveSoftware/Brave-Browser/*/History"]),
    "arc": ("chromium", ["~/Library/Application Support/Arc/User Data/*/History"]),
    "firefox": ("firefox", ["~/Library/Application Support/Firefox/Profiles/*/places.sqlite"]),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read browser SQLite history locally and print only domain visit counts."
    )
    parser.add_argument("--browser", choices=["auto", *MAC_SOURCES], default="auto")
    parser.add_argument("--hours", type=int, default=168)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--min-visits", type=int, default=2)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--history-db", type=Path, help="Explicit database path for testing or unsupported layouts")
    parser.add_argument("--schema", choices=["chromium", "safari", "firefox"])
    args = parser.parse_args()
    if args.hours < 1 or args.hours > 24 * 90:
        parser.error("--hours must be between 1 and 2160")
    if args.limit < 1 or args.limit > 100:
        parser.error("--limit must be between 1 and 100")
    if args.min_visits < 1:
        parser.error("--min-visits must be positive")
    if bool(args.history_db) != bool(args.schema):
        parser.error("--history-db and --schema must be supplied together")
    return args


def normalize_host(raw_url: str) -> str | None:
    try:
        parts = urlsplit(raw_url)
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            return None
        host = parts.hostname.rstrip(".").lower().encode("idna").decode("ascii")
        if host.startswith("www."):
            host = host[4:]
        if host == "localhost" or host.endswith(".local") or "." not in host:
            return None
        try:
            ipaddress.ip_address(host)
            return None
        except ValueError:
            pass
        if len(host) > 253 or any(not label or len(label) > 63 for label in host.split(".")):
            return None
        return host
    except (UnicodeError, ValueError):
        return None


def readonly_connection(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(path.resolve()))}?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=2)


def recent_rows(path: Path, schema: str, cutoff_unix: float):
    conn = readonly_connection(path)
    try:
        if schema == "chromium":
            cutoff = int((cutoff_unix + 11_644_473_600) * 1_000_000)
            query = """
                SELECT urls.url, COUNT(*)
                FROM visits JOIN urls ON visits.url = urls.id
                WHERE visits.visit_time >= ?
                GROUP BY urls.url
            """
        elif schema == "safari":
            cutoff = cutoff_unix - 978_307_200
            query = """
                SELECT history_items.url, COUNT(*)
                FROM history_visits
                JOIN history_items ON history_visits.history_item = history_items.id
                WHERE history_visits.visit_time >= ?
                GROUP BY history_items.url
            """
        else:
            cutoff = int(cutoff_unix * 1_000_000)
            query = """
                SELECT moz_places.url, COUNT(*)
                FROM moz_historyvisits
                JOIN moz_places ON moz_historyvisits.place_id = moz_places.id
                WHERE moz_historyvisits.visit_date >= ?
                GROUP BY moz_places.url
            """
        yield from conn.execute(query, (cutoff,))
    finally:
        conn.close()


def sources(args: argparse.Namespace):
    if args.history_db:
        yield "explicit", args.schema, args.history_db.expanduser()
        return
    names = MAC_SOURCES if args.browser == "auto" else {args.browser: MAC_SOURCES[args.browser]}
    for name, (schema, patterns) in names.items():
        for pattern in patterns:
            for match in sorted(glob.glob(os.path.expanduser(pattern))):
                yield name, schema, Path(match)


def main() -> int:
    args = parse_args()
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=args.hours)).timestamp()
    counts: dict[str, int] = {}
    found = 0
    failures = []
    for source_name, schema, path in sources(args):
        found += 1
        try:
            for raw_url, count in recent_rows(path, schema, cutoff):
                host = normalize_host(raw_url)
                if host:
                    counts[host] = counts.get(host, 0) + int(count)
        except (OSError, sqlite3.Error) as exc:
            failures.append(f"{source_name}: {type(exc).__name__}")

    if found == 0:
        print("No supported browser history database was found.", file=sys.stderr)
        return 3
    for failure in sorted(set(failures)):
        print(f"history source unavailable ({failure}); privacy controls were not bypassed", file=sys.stderr)

    rows = sorted(
        ((host, count) for host, count in counts.items() if count >= args.min_visits),
        key=lambda item: (-item[1], item[0]),
    )[: args.limit]
    if args.json:
        json.dump([{"domain": host, "visits": count} for host, count in rows], sys.stdout)
        sys.stdout.write("\n")
    else:
        print("domain\tvisits")
        for host, count in rows:
            print(f"{host}\t{count}")
    return 0 if rows else 4


if __name__ == "__main__":
    raise SystemExit(main())
