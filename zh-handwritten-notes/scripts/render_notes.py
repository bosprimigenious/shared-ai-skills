#!/usr/bin/env python3
"""Render a .notes.md file as one handwritten notebook PNG."""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError:
    print("Pillow missing. Install in a venv: pip install Pillow", file=sys.stderr)
    sys.exit(2)

HERE = Path(__file__).resolve().parent

import json
import subprocess


def probe_fonts():
    script = HERE / "discover_fonts.py"
    raw = subprocess.check_output([sys.executable, str(script)], text=True)
    data = json.loads(raw)
    if not data.get("ok"):
        raise SystemExit("no usable CJK font; run scripts/discover_fonts.py")
    pref = data["preferred"]
    heading = pref.get("heading") or pref["title"]
    return pref["title"], heading, pref["body"], pref["body_bold"]


PAPERS = {
    "pale": {
        "paper": (254, 253, 249),
        "rule": (236, 232, 224),
        "margin": (220, 176, 176),
        "frame": (210, 200, 188),
        "frame2": (226, 218, 206),
        "header": (198, 148, 148),
    },
    "cream": {
        "paper": (244, 232, 206),
        "rule": (214, 196, 168),
        "margin": (196, 118, 118),
        "frame": (168, 132, 108),
        "frame2": (196, 168, 140),
        "header": (168, 86, 86),
    },
}

INK = (42, 46, 56)
INK_SOFT = (62, 66, 78)
RED = (168, 42, 42)
NAVY = (32, 58, 104)
TEAL = (28, 92, 76)

BAD_START = set("，。；：、）》」』】,.;:!?%？！")
BREAK_AFTER = set("，。；：、？！,.;:!?")
TOKEN_RE = re.compile(
    r"\{x:[^}]+\}|[\u4e00-\u9fff]|[A-Za-z0-9_]+(?:[.=+\-;<>]*)|[`=+\-;<>()\[\]{}]+|."
)
HEAD_NUM = re.compile(r"^(\d+(?:\.\d+)*)\s+(.*)$")
X_MARK = re.compile(r"^\{x:([^}]+)\}$")


def font(path, size, index):
    return ImageFont.truetype(path, size=size, index=index)


def tw(fnt, s):
    if not s:
        return 0.0
    if hasattr(fnt, "getlength"):
        return float(fnt.getlength(s))
    box = fnt.getbbox(s)
    return float(box[2] - box[0])


def tokenize(s):
    return TOKEN_RE.findall(s)


def parse_runs(text, f_reg, f_bold):
    parts = text.split("**")
    runs = []
    for i, part in enumerate(parts):
        if not part:
            continue
        runs.append((part, f_bold if i % 2 == 1 else f_reg))
    return runs


def ink_vary(base, rnd, amp=10):
    return tuple(max(0, min(255, c + rnd.randint(-amp, amp))) for c in base)


class Pen:
    def __init__(self, draw, x0, y0, x1, y_max, line_h, rnd, mess_scale):
        self.draw = draw
        self.x0 = x0
        self.x1 = x1
        self.y = y0
        self.y_max = y_max
        self.line_h = line_h
        self.width = x1 - x0
        self.overflow = False
        self.rnd = rnd
        self.mess_scale = mess_scale
        self.mess = 0.45 * mess_scale
        self.last_kill = None

    def ensure(self, need):
        if self.y + need > self.y_max:
            self.overflow = True
            return False
        return True

    def roll_mess(self):
        r = self.rnd.random()
        if r < 0.22:
            base = self.rnd.uniform(0.08, 0.22)
        elif r < 0.78:
            base = self.rnd.uniform(0.28, 0.62)
        else:
            base = self.rnd.uniform(0.72, 1.15)
        self.mess = base * self.mess_scale

    def draw_glyph(self, ch, fnt, x, y, fill):
        m = self.mess
        jx = self.rnd.uniform(-0.35, 0.5) * (0.4 + m)
        jy = self.rnd.uniform(-0.5, 0.7) * (0.5 + m * 1.4)
        if m > 0.85 and self.rnd.random() < 0.18:
            jy += self.rnd.choice([-3.2, 3.6])
        col = ink_vary(fill, self.rnd, 4 + int(m * 8))
        self.draw.text((x + jx, y + jy), ch, font=fnt, fill=col)
        tracking = self.rnd.uniform(-0.25, 0.35) + (m - 0.4) * self.rnd.uniform(-0.2, 0.6)
        return tw(fnt, ch) + tracking

    def write_chars(self, s, fnt, x, y, fill):
        cx = x
        for ch in s:
            cx += self.draw_glyph(ch, fnt, cx, y, fill)
        return cx

    def wavy_line(self, x0, y, x1, fill, width=2, amp=2.4):
        if x1 <= x0:
            return
        pts = []
        x = x0
        while x < x1:
            pts.append((x, y + self.rnd.uniform(-amp, amp)))
            x += self.rnd.uniform(6, 18)
        pts.append((x1, y + self.rnd.uniform(-amp, amp)))
        if len(pts) >= 2:
            self.draw.line(pts, fill=fill, width=width)

    def strike(self, x0, y, x1, fill=INK):
        col = ink_vary(fill, self.rnd, 8)
        n = self.rnd.randint(1, 2)
        for i in range(n):
            yy = y + 14 + i * self.rnd.uniform(4, 8)
            self.wavy_line(
                x0 + self.rnd.uniform(-4, 3),
                yy,
                x1 + self.rnd.uniform(-2, 8),
                col,
                width=self.rnd.randint(2, 3),
                amp=self.rnd.uniform(1.0, 3.2),
            )

    def scribble(self, x0, y, x1, fill=INK):
        col = ink_vary(fill, self.rnd, 10)
        styles = ["loops", "slashes", "mix", "blob"]
        style = self.rnd.choice([s for s in styles if s != self.last_kill] or styles)
        self.last_kill = style
        ox0 = x0 + self.rnd.uniform(-4, 5)
        ox1 = x1 + self.rnd.uniform(-5, 9)
        if ox1 < ox0 + 10:
            ox1 = ox0 + 10
        self.wavy_line(ox0, y + 16, ox1, col, width=2, amp=2.0)
        if style in ("loops", "mix"):
            for _ in range(self.rnd.randint(2, 5)):
                cx = self.rnd.uniform(ox0, ox1)
                cy = y + 16 + self.rnd.uniform(-6, 8)
                rx = self.rnd.uniform(5, 13)
                ry = self.rnd.uniform(4, 10)
                self.draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=col, width=2)
        if style in ("slashes", "mix", "blob"):
            for _ in range(self.rnd.randint(2, 4)):
                xa = self.rnd.uniform(ox0, ox1)
                self.draw.line(
                    (xa, y + self.rnd.uniform(4, 12), xa + self.rnd.uniform(-4, 16), y + self.rnd.uniform(18, 32)),
                    fill=col,
                    width=2,
                )

    def kill_span(self, x0, y, x1, fill=INK):
        if self.rnd.random() < 0.45:
            self.strike(x0, y, x1, fill)
        else:
            self.scribble(x0, y, x1, fill)

    def flow(self, parts, f_reg, f_bold, fill=INK, indent=0):
        max_w = self.width - indent
        x = self.x0 + indent
        if not self.ensure(self.line_h):
            return
        self.roll_mess()
        y = self.y + self.rnd.uniform(-1.2, 2.0) * self.mess

        def newline():
            nonlocal x, y
            self.y += self.line_h
            if not self.ensure(self.line_h):
                return False
            self.roll_mess()
            x = self.x0 + indent
            y = self.y + self.rnd.uniform(-1.2, 2.0) * self.mess
            return True

        for part in parts:
            kind = part[0]
            if kind == "t":
                _, text, fnt, col = part
                for tok in tokenize(text):
                    if X_MARK.match(tok):
                        continue
                    w = tw(fnt, tok)
                    if x + w > self.x0 + indent + max_w and tok not in BAD_START:
                        if not newline():
                            return
                    x = self.write_chars(tok, fnt, x, y, col)
            elif kind == "x":
                _, wrong, right, rfill = part
                ww = tw(f_reg, wrong) + 8 + tw(f_reg, right)
                if x + ww > self.x0 + indent + max_w:
                    if not newline():
                        return
                x0 = x
                x = self.write_chars(wrong, f_reg, x, y, fill)
                self.kill_span(x0, y, x, fill)
                x += self.rnd.uniform(4, 14)
                cy = y - self.rnd.uniform(0, 6) if self.rnd.random() < 0.3 else y
                x = self.write_chars(right, f_reg, x, cy, rfill)
                x += 2
        self.y += self.line_h

    def heading(self, num, title, f_num, f_title, f_title_b=None):
        """Printed 题目: no jitter, no handwriting face."""
        if not self.ensure(self.line_h + 10):
            return
        prefix = f"{num}  " if num else ""
        px = tw(f_num, prefix) if prefix else 0
        max_w = self.width - px
        lines = []
        cur = ""
        for ch in title:
            if cur and tw(f_title, cur + ch) > max_w:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        if cur:
            lines.append(cur)
        first = True
        for ln in lines or [""]:
            if not self.ensure(self.line_h):
                return
            if first and prefix:
                self.draw.text((self.x0, self.y), prefix, font=f_num, fill=RED)
            x = self.x0 + (px if first else 0)
            self.draw.text((x, self.y), ln, font=f_title, fill=NAVY)
            self.y += self.line_h
            first = False
        self.draw.line(
            (self.x0, self.y - 8, self.x0 + self.width, self.y - 8),
            fill=(210, 176, 168),
            width=1,
        )
        self.y += 6


def parse_inline(text, f_reg, f_bold, fill):
    parts = []
    buf = []

    def flush(bold=False):
        s = "".join(buf)
        buf.clear()
        if s:
            parts.append(("t", s, f_bold if bold else f_reg, fill))

    i = 0
    bold = False
    while i < len(text):
        if text.startswith("**", i):
            flush(bold)
            bold = not bold
            i += 2
            continue
        m = re.match(r"\{x:([^|}]+)\|([^|}]+)(?:\|([^}]+))?\}", text[i:])
        if m:
            flush(bold)
            right_fill = TEAL if (m.group(3) or "").strip().lower() == "teal" else fill
            parts.append(("x", m.group(1), m.group(2), right_fill))
            i += m.end()
            continue
        buf.append(text[i])
        i += 1
    flush(bold)
    return parts


def parse_notes(src: str):
    title = ""
    blocks = []
    for raw in src.splitlines():
        line = raw.rstrip()
        if not line.strip():
            blocks.append(("gap", 10))
            continue
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            rest = line[3:].strip()
            m = HEAD_NUM.match(rest)
            if m:
                blocks.append(("h", m.group(1), m.group(2)))
            else:
                blocks.append(("h", "", rest))
            continue
        if line.startswith("> "):
            blocks.append(("s", line[2:]))
            continue
        if line.startswith("- "):
            blocks.append(("b", line[2:]))
            continue
        blocks.append(("p", line))
    return title, blocks


def paper_bg(w, h, paper, rnd):
    img = Image.new("RGB", (w, h), paper)
    px = img.load()
    for _ in range(w * h // 42):
        x = rnd.randint(0, w - 1)
        y = rnd.randint(0, h - 1)
        d = rnd.randint(-4, 3)
        r, g, b = px[x, y]
        px[x, y] = (
            max(0, min(255, r + d)),
            max(0, min(255, g + d - 1)),
            max(0, min(255, b + d - 1)),
        )
    return img


def render(src: str, out: Path, paper_name: str, mess: float, width: int, seed: int):
    theme = PAPERS[paper_name]
    title_spec, heading_spec, body_spec, bold_spec = probe_fonts()
    w = width
    line_h = 64
    canvas_h = 12000
    margin_l, margin_r, margin_b = 118, 72, 80
    red_x = 86
    rule_origin = 148

    rnd = random.Random(seed)
    img = paper_bg(w, canvas_h, theme["paper"], rnd)
    draw = ImageDraw.Draw(img)

    f_title = font(title_spec["path"], 52, title_spec["index"])
    f_h_num = font(heading_spec["path"], 36, heading_spec["index"])
    f_h = font(heading_spec["path"], 32, heading_spec["index"])
    f_body = font(body_spec["path"], 34, body_spec["index"])
    f_body_b = font(bold_spec["path"], 34, bold_spec["index"])
    f_small = font(body_spec["path"], 31, body_spec["index"])
    f_small_b = font(bold_spec["path"], 31, bold_spec["index"])

    y = rule_origin
    while y < canvas_h - 50:
        draw.line((red_x + 8, y, w - 36, y), fill=theme["rule"], width=1)
        y += line_h
    draw.line((red_x, 120, red_x, canvas_h - 40), fill=theme["margin"], width=2)

    title, blocks = parse_notes(src)
    title_y = 40
    if title:
        hw = tw(f_title, title)
        draw.text(((w - hw) / 2, title_y), title, font=f_title, fill=NAVY)
        tb = f_title.getbbox(title)
        line_y = title_y + tb[3] + 8
    else:
        line_y = 80
    draw.line((120, line_y, w - 120, line_y), fill=theme["header"], width=1)

    col_top = max(rule_origin, line_y + 16)
    P = Pen(draw, margin_l + 8, col_top, w - margin_r, canvas_h - margin_b, line_h, random.Random(seed + 17), mess)

    for blk in blocks:
        if P.overflow:
            break
        kind = blk[0]
        if kind == "gap":
            P.y += blk[1]
        elif kind == "h":
            P.heading(blk[1], blk[2], f_h_num, f_h, f_h)
        elif kind == "s":
            P.flow(parse_inline(blk[1], f_small, f_small_b, INK_SOFT), f_small, f_small_b, INK_SOFT, indent=36)
        elif kind == "b":
            P.flow(parse_inline(blk[1], f_body, f_body_b, INK), f_body, f_body_b, INK, indent=24)
        else:
            P.flow(parse_inline(blk[1], f_body, f_body_b, INK), f_body, f_body_b, INK, indent=12)

    crop_h = min(canvas_h, int(P.y + margin_b))
    img = img.crop((0, 0, w, crop_h))
    img = ImageEnhance.Contrast(img).enhance(1.02)
    img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=45, threshold=2))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(
        json.dumps(
            {
                "out": str(out),
                "size": list(img.size),
                "overflow": P.overflow,
                "paper": paper_name,
                "title_font": title_spec,
                "heading_font": heading_spec,
                "body_font": body_spec,
                "bytes": out.stat().st_size,
            },
            ensure_ascii=False,
        )
    )


def main():
    ap = argparse.ArgumentParser(description="Render handwritten Chinese notes PNG")
    ap.add_argument("input", help=".notes.md file")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--paper", choices=sorted(PAPERS), default="pale")
    ap.add_argument("--mess", type=float, default=0.55)
    ap.add_argument("--width", type=int, default=1860)
    ap.add_argument("--seed", type=int, default=29)
    args = ap.parse_args()
    src = Path(args.input).read_text(encoding="utf-8")
    render(src, Path(args.out), args.paper, args.mess, args.width, args.seed)


if __name__ == "__main__":
    main()
