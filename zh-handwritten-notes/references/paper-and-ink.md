# Paper and ink

## Paper

Default `--paper pale`:

| Token | RGB | Role |
|---|---|---|
| Paper | `(254, 253, 249)` | Almost white, hint of yellow |
| Rule | `(236, 232, 224)` | Faint college rule |
| Margin | `(220, 176, 176)` | Thin red margin |
| Frame | `(210, 200, 188)` | Light |

`--paper cream` is the older tan pad `(244, 232, 206)`. Only use it when the user wants a darker notebook. If they say 白底 / 淡一点, stay on pale.

Grain: sparse, ΔRGB ±3. Heavy fiber noise reads as stained kraft.

## Ink

| Token | RGB |
|---|---|
| Body | `(42, 46, 56)` |
| Soft | `(62, 66, 78)` |
| Heading number | `(168, 42, 42)` |
| Heading text | `(32, 58, 104)` |
| Stage / correction accent | `(28, 92, 76)` |

Do not boost contrast after render; it yellows pale paper.

## Geometry

- Width ~1860 px
- `LINE_H` 58, left content margin ~118, red margin ~86
- Canvas height may be 8000+; **crop** to last ink + ~80 px
- **No outer frame.** Crop only; do not redraw a brown rectangle
- One column. Two-column A3 left a dead band on real homework pages
