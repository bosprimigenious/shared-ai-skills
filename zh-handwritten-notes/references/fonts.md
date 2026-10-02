# Fonts

Chinese on the page must come from a real font file. Probe first.

```bash
python3 scripts/discover_fonts.py
```

## macOS (preferred)

`discover_fonts.py` walks Font8 / system fonts. Do not hard-code the `AssetsV2/…/<hash>` path.

| Role | File | Index | Face | Why |
|---|---|---|---|---|
| Page title | `PingFang.ttc` | **4** | PingFang SC Medium | printed, not handwriting |
| 题目 (`##`) | `Songti.ttc` | **0** | Songti SC | printed exam/homework stem |
| Body | `Xingkai.ttc` | **0** | STXingkai | 行楷, messier than 翩翩体/手札体 |
| Body emphasis | `Xingkai.ttc` | **1** | same family | no separate bold |

HanziPen / Hannotate look too tidy for “手写作业”. Do not use them for body unless Xingkai is missing.

Always draw a canary `编译原理` and reject a TTC index that drops simplified glyphs.

## Fallbacks (in order)

1. Hannotate SC + HanziPen SC (above)
2. `STXingkai.ttc` / 华文行楷 — denser, still handwriting-like
3. `PingFang.ttc` SC — readable, not very “notes”
4. Noto Sans CJK / Source Han Sans — last resort; say so in the reply

Keep the intended size if you fall back. Do not shrink the layout because the fallback metrics differ; re-wrap.

## Other platforms

There is no Hannotate on Linux/Windows. Use a bundled or user-provided handwriting font (`LXGWWenKai`, `MaShanZheng`, `ZCOOL XiaoWei`) and record the path. If none can draw `编译`, stop and ask; do not emit an image model page.
