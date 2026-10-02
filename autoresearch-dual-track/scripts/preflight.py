#!/usr/bin/env python3
"""Validate that an AutoResearch task contract is ready for paid long runs."""

import argparse
import json
from pathlib import Path


def nested(data, *keys):
    value = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def validate(data: dict) -> list[str]:
    errors = []
    required = [
        (("task_id",), "task_id"),
        (("metric", "name"), "metric.name"),
        (("metric", "direction"), "metric.direction"),
        (("acceptance", "improvement_threshold"), "acceptance.improvement_threshold"),
        (("acceptance", "randomness_protocol"), "acceptance.randomness_protocol"),
        (("infrastructure", "development_runtime"), "infrastructure.development_runtime"),
        (("infrastructure", "target_harness"), "infrastructure.target_harness"),
        (("infrastructure", "target_backend"), "infrastructure.target_backend"),
        (("infrastructure", "backend_gpu_support_evidence"), "infrastructure.backend_gpu_support_evidence"),
        (("infrastructure", "persistent_snapshot"), "infrastructure.persistent_snapshot"),
        (("cost", "stop_loss"), "cost.stop_loss"),
    ]
    for keys, label in required:
        value = nested(data, *keys)
        if value is None or value == "" or (isinstance(value, str) and "replace" in value):
            errors.append(f"missing or placeholder: {label}")
    tracks = data.get("agent_tracks")
    if not isinstance(tracks, list) or len(tracks) != 2 or len(set(tracks)) != 2:
        errors.append("agent_tracks must contain exactly two distinct tracks")
    if not data.get("requires_gpu"):
        errors = [item for item in errors if "backend_gpu_support_evidence" not in item]
    if nested(data, "metric", "direction") not in {"minimize", "maximize"}:
        errors.append("metric.direction must be minimize or maximize")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    data = json.loads(args.contract.read_text(encoding="utf-8"))
    errors = validate(data)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
