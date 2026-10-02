#!/usr/bin/env python3
"""Deterministically arrange portrait images as overlapping paper cards."""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SIZES = {"landscape": (3840, 2160), "portrait": (2160, 3840)}


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", nargs="+", type=Path, required=True)
    p.add_argument("--front", nargs="+", type=int, required=True)
    p.add_argument("--back", nargs="+", type=int, required=True)
    p.add_argument("--topmost", type=int, required=True)
    p.add_argument("--orientation", choices=SIZES, default="landscape")
    p.add_argument("--output", type=Path, required=True)
    return p.parse_args()


def validate(a):
    expected = set(range(1, len(a.inputs) + 1))
    if set(a.front) & set(a.back) or set(a.front) | set(a.back) != expected:
        raise SystemExit("--front and --back must cover every input exactly once")
    if a.topmost not in a.front:
        raise SystemExit("--topmost must belong to --front")
    for path in a.inputs:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
        try:
            with Image.open(path) as im:
                im.verify()
        except Exception as exc:
            raise SystemExit(f"cannot decode {path}: {exc}") from exc


def background(size):
    base = Image.new("RGBA", size, (8, 14, 36, 255))
    glow = Image.new("RGBA", size)
    d = ImageDraw.Draw(glow)
    w, h = size
    d.ellipse((w * .10, h * .35, w * .90, h * 1.15), fill=(160, 105, 55, 36))
    return Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(min(size) // 8)))


def make_card(path, width, angle):
    art = Image.open(path).convert("RGB")
    art = art.resize((width, round(width * art.height / art.width)), Image.Resampling.LANCZOS)
    border = max(14, round(width * .028))
    out = Image.new("RGBA", (art.width + 2 * border, art.height + 2 * border), (239, 235, 220, 255))
    out.alpha_composite(art.convert("RGBA"), (border, border))
    ImageDraw.Draw(out).rectangle((1, 1, out.width - 2, out.height - 2), outline=(202, 190, 162, 255), width=max(2, border // 8))
    return out.rotate(angle, Image.Resampling.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))


def paste(canvas, item, xy):
    shadow = Image.new("RGBA", item.size)
    alpha = item.getchannel("A").filter(ImageFilter.GaussianBlur(34))
    shadow.putalpha(alpha.point(lambda p: int(p * .58)))
    canvas.alpha_composite(shadow, (xy[0] + 28, xy[1] + 40))
    canvas.alpha_composite(item, xy)


def positions(n, y, width, canvas_w, span):
    if n == 1:
        return [((canvas_w - width) // 2, y)]
    left = int(canvas_w * (1 - span) / 2)
    right = int(canvas_w * (1 + span) / 2 - width)
    return [(round(left + i * (right - left) / (n - 1)), y + (120 if i not in (n // 2,) else 0)) for i in range(n)]


def main():
    a = args()
    validate(a)
    size = SIZES[a.orientation]
    w, h = size
    canvas = background(size)
    back_w = round(w * (.18 if a.orientation == "landscape" else .24))
    front_w = round(w * (.235 if a.orientation == "landscape" else .31))
    back_y = round(h * (.32 if a.orientation == "landscape" else .43))
    front_y = round(h * (.07 if a.orientation == "landscape" else .16))

    for i, (idx, xy) in enumerate(zip(a.back, positions(len(a.back), back_y, back_w, w, .90))):
        paste(canvas, make_card(a.inputs[idx - 1], back_w, (i - (len(a.back) - 1) / 2) * 6), xy)

    front_pos = dict(zip(a.front, positions(len(a.front), front_y, front_w, w, .67)))
    for idx in (x for x in a.front if x != a.topmost):
        rank = a.front.index(idx)
        paste(canvas, make_card(a.inputs[idx - 1], front_w, (rank - (len(a.front) - 1) / 2) * 5.5), front_pos[idx])

    top_w = round(front_w * 1.07)
    paste(canvas, make_card(a.inputs[a.topmost - 1], top_w, 0), ((w - top_w) // 2, max(40, front_y - round(h * .05))))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(a.output, "PNG", optimize=True)
    print(f"saved={a.output.resolve()}")
    print(f"size={w}x{h}")


if __name__ == "__main__":
    main()
