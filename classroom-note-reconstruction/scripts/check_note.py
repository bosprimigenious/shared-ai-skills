#!/usr/bin/env python3
"""Fail-closed checks for timeline correspondence, cues, locators, and meta."""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "check_framework_map", ROOT / "check_framework_map.py"
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["check_framework_map"] = mod
spec.loader.exec_module(mod)

META_PATTERNS = (
    re.compile(r"本节课将学习"),
    re.compile(r"以下是笔记内容"),
    re.compile(r"本笔记基于"),
    re.compile(r"根据\s*ASR"),
    re.compile(r"从幻灯片中可以看到"),
)
LOCATOR = re.compile(
    r"(?:P\d{2,}|\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)",
    re.IGNORECASE,
)
SECTION_REF = re.compile(r"3\.\d+")
SUBHEAD = re.compile(r"^###\s+(3\.\d+)\b.*$", re.MULTILINE)
CUE = re.compile(r"本节问题[：:]")
SOURCE_LINE = re.compile(r"来源[：:]")


def region(src: str, heading_pat: str, stop_pat: str | None = None) -> str:
    m = re.search(heading_pat, src, re.MULTILINE)
    if not m:
        return ""
    rest = src[m.end() :]
    if stop_pat:
        n = re.search(stop_pat, rest, re.MULTILINE)
        if n:
            rest = rest[: n.start()]
    return rest


def check_timeline(src: str) -> list[str]:
    errors: list[str] = []
    body = region(src, r"^###\s+2\.1\b", r"^###\s+")
    if not body.strip():
        return ["缺少 2.1 原初推进路线"]
    refs = SECTION_REF.findall(body)
    locs = LOCATOR.findall(body)
    if len(refs) < 2:
        errors.append("2.1 至少两行需指向 3.x 小节")
    if len(locs) < 2:
        errors.append("2.1 至少两行需有时间戳或 P 号")
    heads = {m.group(1) for m in SUBHEAD.finditer(src)}
    missing = sorted(set(refs) - heads)
    if missing:
        errors.append(f"2.1 指向不存在的小节：{', '.join(missing)}")
    return errors


def check_sections(src: str) -> list[str]:
    errors: list[str] = []
    body = region(src, r"^##\s+3[\s.．]", r"^##\s+(?!3)")
    if not body.strip():
        return ["缺少第 3 节分节内容"]
    matches = list(SUBHEAD.finditer(src))
    if len(matches) < 2:
        errors.append("第 3 节至少两个 3.x 小节")
        return errors
    for i, m in enumerate(matches):
        start = m.end()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            nxt = re.search(r"^##\s+", src[start:], re.MULTILINE)
            end = start + nxt.start() if nxt else len(src)
        chunk = src[start:end]
        first_lines = "\n".join(chunk.strip().splitlines()[:8])
        if not CUE.search(first_lines):
            errors.append(f"{m.group(1)} 标题下缺少「本节问题」")
        if not (SOURCE_LINE.search(first_lines) or LOCATOR.search(first_lines)):
            errors.append(f"{m.group(1)} 标题下缺少来源行或定位号")
        if CUE.search(first_lines):
            cue_line = next(
                (ln for ln in first_lines.splitlines() if CUE.search(ln)), ""
            )
            q = CUE.sub("", cue_line).strip()
            if q and not re.search(r"[？?如何为何为什么怎样]", q):
                errors.append(f"{m.group(1)} 本节问题不是问句：「{q}」")
    return errors


def check_meta(src: str) -> list[str]:
    errors = []
    for pat in META_PATTERNS:
        if pat.search(src):
            errors.append(f"含笔记过程套话：{pat.pattern}")
    return errors


def check_note(src: str) -> list[str]:
    errors = []
    errors.extend(mod.check_note(src))
    errors.extend(check_timeline(src))
    errors.extend(check_sections(src))
    errors.extend(check_meta(src))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--expect-fail", action="store_true")
    args = ap.parse_args()
    src = Path(args.path).read_text(encoding="utf-8")
    errors = check_note(src)
    failed = bool(errors)
    if args.expect_fail:
        if failed:
            print(f"OK (expected fail): {args.path}")
            for e in errors:
                print(f"  - {e}")
            return 0
        print(f"FAIL: {args.path} 本应违规却通过")
        return 1
    if failed:
        print(f"FAIL: {args.path}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
