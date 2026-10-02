# Chinese Handwritten Notes

> Generate authentic Chinese handwritten homework or notebook pages as a long single-column PNG, using real CJK handwriting fonts (not an image model for the glyphs). Use when the user asks for 手写作业, 手写笔记, 手写体答案, 潦草涂改, 手札体, 翩翩体, or a ruled-notebook image of answers.

Turn locked answer text into a **long ruled notebook PNG**. Chinese glyphs come from real fonts on disk. An image model may only paint paper texture or non-text decoration.

## Core Rule

Do not let an image model be the source of Chinese characters. Dense CJK from `image_gen` / GPT Image will be wrong strokes, wrong variants, or pseudo-Han. Render 题目 with a printed face (Songti / PingFang) and body with a messy 行楷 (STXingkai on macOS, or Noto / LXGW fallback). Final readable answers stay lecture-correct even when the page has strikeouts.

This skill is for **new handwritten pages**. Repairing a photo of existing notes, a poster, or a diagram is `image-text-restore`.

## When to use

- 手写作业 / 手写笔记 / 一页答案
- 要潦草、涂改、错别字再改，但最后能读的答案是对的
- 白纸微黄横线本，单栏可以很长，不要两栏

Do **not** use for: posters, UI, architecture diagrams, restoring blurry screenshots.

## Default deliverable

One PNG, single column, crop to content (no huge empty tail).

| Default | Value |
|---|---|
| Width | ~1860 px |
| Height | canvas tall, then crop to last ink + margin |
| Paper | almost white, hint of warm yellow `(254, 253, 249)` |
| Layout | one column, college-ruled, faint red margin, **no outer frame** |
| Title | user title only; no “手写笔记·1.1–1.7”, no font-name footer |
| Path | user-given folder if any; otherwise say the absolute path |

## Workflow

### 1. Lock the text source of truth

Before drawing:

- Answers come from the user, the lecture PDF, or an already-checked draft.
- If the user asked to verify against slides, read those PDFs and correct the draft first.
- Keep a short table of **final** wording. Strikeouts may show an earlier wrong word; the word after the scribble must match the table.

Do not invent course facts to fill the page.

### 2. Probe fonts (do not guess indices)

```bash
python3 scripts/discover_fonts.py
```

On macOS, Apple handwriting TTCs often ship Traditional and Simplified in the same file. **TC indices can miss simplified glyphs.** Prefer:

- 题目 / page title: **printed** Songti SC or PingFang SC — not a handwriting face
- Body: **STXingkai** (`Xingkai.ttc` index **0**) — 行楷, messier than 翩翩体
- No outer page frame. Keep faint rules + red margin.

If those assets are missing, use the first discovered font that can draw `编译` without `.notdef`. Record the actual path and index in the reply. Do not silently switch to a Latin-only font.

### 3. Write a notes source file

Use the markup in [references/note-markup.md](references/note-markup.md). Keep content in a `.notes.md` next to the output, so a later pass can re-render without guessing pixels.

Inline correction, not a lonely numbered line:

```text
两种翻译方式：{x:编译程序|编译方式}和解释方式。
```

### 4. Render with the bundled script

```bash
python3 scripts/render_notes.py path/to/page.notes.md -o path/to/page.png
python3 scripts/render_notes.py path/to/page.notes.md -o path/to/page.png --paper pale --mess 0.55
```

- `--paper pale` (default): white + tiny yellow. `--paper cream` only if the user wants a darker notebook.
- `--mess` 0–1: per-line jitter. 0.45–0.6 looks like notes; 0.9 looks drunk. Do not apply the same scribble template to every correction.
- Single column. Two-column A3 leaves a dead band; do not do it unless asked.

Read [references/paper-and-ink.md](references/paper-and-ink.md) and [references/authenticity.md](references/authenticity.md) before changing look.

### 5. Inspect crops, not only the full page

The long PNG will look fine when fit-to-screen and still be wrong. Crop:

- title + first heading
- one dense body block
- every `{x:…|…}` correction
- the last 400 px (empty tail? clipped glyph? leftover branding?)

Check:

- Simplified characters are complete (not TC `.notdef` boxes)
- Strikeouts are visible but the **correction** is readable
- No footer “第1页 / 手札体／翩翩体”
- Paper is pale if that was requested
- Scribbles are not identical ellipses on a grid

If a crop fails, change the source file or flags and re-render. Do not “fix Chinese” with an image model.

### 6. Copy to an openable path

Chat `images/…` paths are often not openable in Finder. Copy to the folder the user named (class notes, Desktop, etc.) and tell them that absolute path.

## Authenticity (only if asked)

User says 潦草 / 涂改 / 错别字:

- Corrections sit **in the sentence**.
- Vary kill style (one line, two lines, a few loops). Do not tile the same loops.
- Per-line mess factor: some lines almost neat, a few sloppy.
- Do not put `3.` on its own line and the scribble on the next. That looks generated.
- Leave **zero** uncorrected errors in the final readable answer.

If they did not ask for mess, render clean handwriting.

## Hard Stops

- Image model as the CJK text layer
- Traditional TTC index for simplified homework
- Dark tan paper when they asked 白底
- Branding footer, “手写笔记·题号范围”, font-name caption
- Outer page frame / brown double border
- Two columns by default
- Uniform jitter / identical scribbles on every fix
- Changing locked answers silently
- `pip install` onto the global interpreter; use the machine’s existing Pillow or a venv

## Quality Checks

- [ ] Text source of truth exists (user / slides / checked draft)
- [ ] `discover_fonts.py` ran; actual font path + index recorded
- [ ] Rendered with `scripts/render_notes.py`, not an image model
- [ ] Single column, cropped to content
- [ ] Paper matches the request (pale default)
- [ ] Crops of title, body, corrections, and tail inspected
- [ ] Final readable answers match the locked table
- [ ] Finder-openable path given

## Conflict with image-text-restore

| Ask | Skill |
|---|---|
| New 手写作业 / 笔记 PNG | **this skill** |
| Existing image, 中文糊 / 错字 / 放大保字 | `image-text-restore` |

## References

- [references/note-markup.md](references/note-markup.md)
- [references/fonts.md](references/fonts.md)
- [references/paper-and-ink.md](references/paper-and-ink.md)
- [references/authenticity.md](references/authenticity.md)
