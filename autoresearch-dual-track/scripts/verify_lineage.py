#!/usr/bin/env python3
"""Reject formal result indexes that splice identities across trials."""

import argparse
import json
import re
from pathlib import Path


HASH = re.compile(r"^[0-9a-f]{64}$")


def validate(data: dict) -> list[str]:
    errors = []
    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        return ["runs must be a non-empty list"]
    seen_ids = set()
    seen_pairs = set()
    required = {"run_id", "role", "training_seed", "replicate_id", "source_sha256", "config_sha256", "receipt_run_id", "artifact_run_id"}
    for index, run in enumerate(runs):
        prefix = f"runs[{index}]"
        if not isinstance(run, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(required - set(run))
        if missing:
            errors.append(f"{prefix} missing: {', '.join(missing)}")
            continue
        run_id = run["run_id"]
        if run_id in seen_ids:
            errors.append(f"duplicate run_id: {run_id}")
        seen_ids.add(run_id)
        pair = (run["role"], run["training_seed"], run["replicate_id"])
        if pair in seen_pairs:
            errors.append(f"duplicate role/seed/replicate: {pair}")
        seen_pairs.add(pair)
        for field in ("receipt_run_id", "artifact_run_id"):
            if run[field] != run_id:
                errors.append(f"{prefix}.{field} does not match run_id")
        for field in ("source_sha256", "config_sha256"):
            if not isinstance(run[field], str) or not HASH.fullmatch(run[field]):
                errors.append(f"{prefix}.{field} must be a lowercase SHA-256")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    args = parser.parse_args()
    data = json.loads(args.index.read_text(encoding="utf-8"))
    errors = validate(data)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
