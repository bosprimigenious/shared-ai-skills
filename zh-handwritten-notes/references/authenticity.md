# Authenticity

Only when the user asks for 潦草 / 涂改 / 错别字. Otherwise keep the hand steady.

## What failed in earlier pages

- Every correction on its own line after a lone `3.` — looks like a template
- The same loop-ellipse tiled across every killed word
- The same jitter amplitude on every glyph
- Strike so light that `调式调试` reads as two words
- Dark tan paper plus identical scribbles — “AI notebook”

## Rules that hold up

1. **Inline.** `{x:五个阶段|六个阶段}` sits in the sentence.
2. **Vary the kill.** One word gets a single stroke, another gets two, another a few loops. Do not reuse the last style.
3. **Per-line mess.** Roll a factor each line: ~20% almost neat, ~55% ordinary, ~25% sloppy. A few characters jump; most do not.
4. **Overshoot.** Strikes may start a few pixels left or run past the last glyph. They must still cover the wrong word.
5. **Readable correction.** After the scribble, the new word is darker/clear and matches the locked answer.
6. **No leftover wrong finals.** A visible `语意` is fine only if `语义` follows and is the one a reader takes.

## Intensity

| `--mess` | Look |
|---|---|
| 0.0–0.2 | Clean notes |
| 0.45–0.6 | Default when they asked for 潦草 |
| ≥ 0.85 | Unreadable; do not ship |
