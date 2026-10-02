# Chinese Handwritten Notes

A Codex / Claude / Grok skill that turns locked answer text into a **long ruled notebook PNG**. 题目 use a printed face; body uses a messy 行楷 from a real font file. An image model is not the source of the characters.

It exists because dense CJK from image generators is the wrong tool: broken radicals, Traditional faces missing simplified glyphs, and “handwritten” pages that still look typeset.

## Install

Ask Codex:

```text
Use $skill-installer to install the skill from
https://github.com/bosprimigenious/zh-handwritten-notes-skill
```

Or clone it:

```bash
git clone https://github.com/bosprimigenious/zh-handwritten-notes-skill.git \
  ~/.codex/skills/zh-handwritten-notes
```

Needs Python 3 and Pillow (`pip install Pillow` in a venv). Restart the agent after installing.

## Use

```text
Use $zh-handwritten-notes to render these answers as one long handwritten
notebook page. Pale paper, single column, real CJK fonts. I want a few
strikeouts, but the final readable answers stay as I wrote them.
```

## Render without an agent

```bash
python3 scripts/discover_fonts.py
python3 scripts/render_notes.py examples/sample.notes.md -o /tmp/notes.png
python3 scripts/render_notes.py examples/sample.notes.md -o /tmp/notes.png --paper pale --mess 0.55
```

Markup: `#` title, `## 1.1 题干` heading, `{x:错|对}` inline correction. See `references/note-markup.md`.

## Hard rules

- Do not use an image model as the Chinese text layer
- 题目: Songti SC / PingFang SC (printed). Body: STXingkai (行楷), not 翩翩体
- No outer page frame; faint rules + red margin only
- Default paper is almost white, not kraft tan
- One column, crop to content
- Strikeouts may show a wrong word; the word after the scribble is the answer

## License

MIT
