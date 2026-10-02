#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Render and validate policy-driven Mihomo/Nyanpasu configuration."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
import re
import sys
from typing import Any

import yaml


ALIAS_PATTERN = re.compile(r"(?:^|[ \t])[&*][A-Za-z0-9_-]+")


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected a YAML mapping: {path}")
    return value


def dump_yaml(value: dict[str, Any]) -> str:
    return yaml.dump(
        value,
        Dumper=NoAliasSafeDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )


def ordered_specs(policy: dict[str, Any]) -> list[dict[str, Any]]:
    specs = policy["groups"]
    by_name = {spec["name"]: spec for spec in specs}
    ordered = []
    for name in policy.get("rule_order") or []:
        if name not in by_name:
            raise ValueError(f"rule_order references unknown group {name}")
        ordered.append(by_name[name])
    ordered.extend(spec for spec in specs if spec["name"] not in (policy.get("rule_order") or []))
    return ordered


def priority_rules(policy: dict[str, Any]) -> list[str]:
    rules = list(policy.get("direct_rules") or [])
    for spec in ordered_specs(policy):
        rules.extend(spec.get("rules") or [])
    return rules


def render(args: argparse.Namespace) -> int:
    config = load_yaml(args.active_config)
    merge = load_yaml(args.merge_config)
    policy = load_yaml(args.policy)
    if policy.get("version") != 1:
        raise ValueError("unsupported policy version")

    groups = config["proxy-groups"]
    specs = policy["groups"]
    defaults = policy["defaults"]
    metadata_patterns = [re.compile(value) for value in (policy.get("metadata_proxy_patterns") or [])]
    all_group_names = {group["name"] for group in groups} | {spec["name"] for spec in specs}

    def clean_candidates(items: list[str] | None) -> list[str]:
        return list(
            dict.fromkeys(
                item
                for item in (items or [])
                if item not in all_group_names
                and not any(pattern.search(item) for pattern in metadata_patterns)
            )
        )

    managed_names = {spec["name"] for spec in specs}
    persisted_groups = []
    persisted_filters = []

    for spec in specs:
        name = spec["name"]
        group = next((item for item in groups if item["name"] == name), None)
        if group is None:
            source_name = spec.get("source_group")
            if not source_name:
                raise ValueError(f"missing group {name} and no source_group was provided")
            source = next((item for item in groups if item["name"] == source_name), None)
            if source is None:
                raise ValueError(f"missing source group {source_name} for {name}")
            group = {"name": name, "proxies": clean_candidates(source["proxies"])}
            groups.insert(0, group)

        candidates = clean_candidates(group["proxies"])
        if not candidates:
            raise ValueError(f"group {name} has no physical candidates")

        group.update(
            {
                "proxies": candidates,
                "type": "url-test",
                "url": spec["url"],
                "interval": spec.get("interval", defaults["interval"]),
                "tolerance": spec.get("tolerance", defaults["tolerance"]),
                "lazy": spec.get("lazy", defaults["lazy"]),
            }
        )

        mode = spec["persist"]
        if mode == "prepend":
            persisted_groups.append(copy.deepcopy(group))
        elif mode == "filter":
            persisted_filters.append(
                {
                    "when": f"item.name == '{name}'",
                    "merge": copy.deepcopy({key: value for key, value in group.items() if key != "name"}),
                }
            )
        else:
            raise ValueError(f"unknown persistence mode for {name}")

    rules = priority_rules(policy)
    config["rules"] = rules + [rule for rule in config["rules"] if rule not in rules]

    existing_prepend = [
        group for group in (merge.get("prepend-proxy-groups") or []) if group.get("name") not in managed_names
    ]
    merge["prepend-proxy-groups"] = copy.deepcopy(existing_prepend + persisted_groups)

    existing_filters = [
        item
        for item in (merge.get("filter__proxy-groups") or [])
        if not any(item.get("when") == f"item.name == '{name}'" for name in managed_names)
    ]
    merge["filter__proxy-groups"] = copy.deepcopy(existing_filters + persisted_filters)

    existing_rules = merge.get("prepend-rules") or []
    merge["prepend-rules"] = rules + [rule for rule in existing_rules if rule not in rules]

    config_yaml = dump_yaml(config)
    merge_yaml = dump_yaml(merge)
    if ALIAS_PATTERN.search(config_yaml) or ALIAS_PATTERN.search(merge_yaml):
        raise ValueError("refusing to write YAML aliases")

    args.out_config.write_text(config_yaml, encoding="utf-8")
    args.out_merge.write_text(merge_yaml, encoding="utf-8")

    for spec in specs:
        group = next(item for item in groups if item["name"] == spec["name"])
        print("\t".join(map(str, [group["name"], group["type"], len(group["proxies"]), group["interval"], group["url"]])))
    print(f"priority_rules\t{len(rules)}")
    return 0


def validate(args: argparse.Namespace) -> int:
    config = load_yaml(args.active_config)
    merge = load_yaml(args.merge_config)
    policy = load_yaml(args.policy)
    errors = []

    groups = config["proxy-groups"]
    group_names = {group["name"] for group in groups}
    specs = policy["groups"]
    defaults = policy["defaults"]
    metadata_patterns = [re.compile(value) for value in (policy.get("metadata_proxy_patterns") or [])]

    for spec in specs:
        name = spec["name"]
        group = next((item for item in groups if item["name"] == name), None)
        if group is None:
            errors.append(f"missing active group: {name}")
            continue
        expected = {
            "type": "url-test",
            "url": spec["url"],
            "interval": spec.get("interval", defaults["interval"]),
            "tolerance": spec.get("tolerance", defaults["tolerance"]),
            "lazy": spec.get("lazy", defaults["lazy"]),
        }
        for key, value in expected.items():
            if group.get(key) != value:
                errors.append(f"{name}.{key}: expected {value!r}, got {group.get(key)!r}")

        candidates = group.get("proxies") or []
        if not candidates:
            errors.append(f"{name}: no candidates")
        for candidate in candidates:
            if candidate in group_names:
                errors.append(f"{name}: nested group candidate {candidate}")
            if any(pattern.search(candidate) for pattern in metadata_patterns):
                errors.append(f"{name}: metadata candidate {candidate}")

    rules = priority_rules(policy)
    if config["rules"][: len(rules)] != rules:
        errors.append("active priority rule order differs from policy")

    prepend_names = [group.get("name") for group in (merge.get("prepend-proxy-groups") or [])]
    filter_conditions = [item.get("when") for item in (merge.get("filter__proxy-groups") or [])]
    for spec in specs:
        name = spec["name"]
        if spec["persist"] == "prepend" and name not in prepend_names:
            errors.append(f"missing persisted prepend group: {name}")
        elif spec["persist"] == "filter":
            condition = f"item.name == '{name}'"
            if condition not in filter_conditions:
                errors.append(f"missing persisted filter: {name}")

    if (merge.get("prepend-rules") or [])[: len(rules)] != rules:
        errors.append("persistent priority rule order differs from policy")
    if "secret" in merge:
        errors.append("merge unexpectedly contains controller secret")
    if ALIAS_PATTERN.search(args.active_config.read_text(encoding="utf-8")):
        errors.append("active config contains YAML aliases")
    if ALIAS_PATTERN.search(args.merge_config.read_text(encoding="utf-8")):
        errors.append("merge config contains YAML aliases")

    if errors:
        print("\n".join(f"ERROR {error}" for error in errors), file=sys.stderr)
        return 1
    print(
        f"VALID groups={len(specs)} priority_rules={len(rules)} "
        f"prepend_groups={len(prepend_names)} filters={len(filter_conditions)}"
    )
    return 0


def chain(args: argparse.Namespace) -> int:
    profiles = load_yaml(args.profiles_config)
    values = profiles.get("chain") or []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list) or not values or not str(values[0]):
        raise ValueError("no persistent merge in profiles.chain")
    print(values[0])
    return 0


def probes(args: argparse.Namespace) -> int:
    policy = load_yaml(args.policy)
    groups = policy.get("groups") or []
    if not isinstance(groups, list):
        raise ValueError("policy groups must be a list")
    for group in groups:
        print(f"{group['name']}\t{group['url']}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    render_parser = commands.add_parser("render")
    render_parser.add_argument("active_config", type=Path)
    render_parser.add_argument("merge_config", type=Path)
    render_parser.add_argument("policy", type=Path)
    render_parser.add_argument("out_config", type=Path)
    render_parser.add_argument("out_merge", type=Path)
    render_parser.set_defaults(handler=render)

    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("active_config", type=Path)
    validate_parser.add_argument("merge_config", type=Path)
    validate_parser.add_argument("policy", type=Path)
    validate_parser.set_defaults(handler=validate)

    chain_parser = commands.add_parser("chain")
    chain_parser.add_argument("profiles_config", type=Path)
    chain_parser.set_defaults(handler=chain)

    probes_parser = commands.add_parser("probes")
    probes_parser.add_argument("policy", type=Path)
    probes_parser.set_defaults(handler=probes)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (KeyError, OSError, re.error, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
