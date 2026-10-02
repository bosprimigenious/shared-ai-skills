#!/usr/bin/env python3
"""Probe CJK fonts: printed face for 题目, messy 行楷 for body."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow missing. Install in a venv: pip install Pillow", file=sys.stderr)
    sys.exit(2)

CANARY = "编译原理"


def can_draw(path: str, index: int) -> bool:
    try:
        fnt = ImageFont.truetype(path, size=32, index=index)
    except OSError:
        return False
    img = Image.new("L", (400, 60), 255)
    draw = ImageDraw.Draw(img)
    draw.text((4, 4), CANARY, font=fnt, fill=0)
    ink = sum(1 for p in img.tobytes() if p < 200)
    return ink > 80


PREFERRED_NAMES = (
    "Xingkai.ttc",
    "STXingkai.ttc",
    "Songti.ttc",
    "PingFang.ttc",
    "Hanzipen.ttc",
    "Hannotate.ttc",
)


def walk_named(root: Path):
    if not root.exists():
        return
    for name in PREFERRED_NAMES:
        yield from root.rglob(name)


def collect(path: Path):
    hits = []
    name = path.name.lower()
    for idx in range(0, 12):
        if can_draw(str(path), idx):
            hits.append({"path": str(path), "index": idx, "file": path.name})
        elif idx >= 3 and "pingfang" not in name and "songti" not in name:
            break
    return hits


def pick(hits, pred):
    for h in hits:
        if pred(h):
            return h
    return None


def main():
    roots = [
        Path("/System/Library/AssetsV2/com_apple_MobileAsset_Font8"),
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"),
    ]
    extra = os.environ.get("NOTES_FONT_DIR")
    if extra:
        roots.append(Path(extra))

    hits = []
    seen = set()
    for root in roots:
        for path in walk_named(root):
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            hits.extend(collect(path))

    heading = pick(hits, lambda h: "songti" in h["file"].lower() and h["index"] == 0) or pick(
        hits, lambda h: "pingfang" in h["file"].lower() and h["index"] == 0
    )
    title = pick(hits, lambda h: "pingfang" in h["file"].lower() and h["index"] == 4) or heading
    body = pick(hits, lambda h: "xingkai" in h["file"].lower() and h["index"] == 0) or pick(
        hits, lambda h: "xingkai" in h["file"].lower()
    ) or pick(hits, lambda h: "hanzipen" in h["file"].lower() and h["index"] == 0)
    body_b = pick(hits, lambda h: "xingkai" in h["file"].lower() and h["index"] == 1) or body

    preferred = {
        "title": title or (hits[0] if hits else None),
        "heading": heading or title or (hits[0] if hits else None),
        "body": body or (hits[0] if hits else None),
        "body_bold": body_b or body or (hits[0] if hits else None),
    }
    out = {"ok": bool(hits), "canary": CANARY, "preferred": preferred, "hits": hits[:40]}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if hits else 1)


if __name__ == "__main__":
    main()
