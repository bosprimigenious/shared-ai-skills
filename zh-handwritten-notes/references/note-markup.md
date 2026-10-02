# Notes markup

Input to `scripts/render_notes.py` is UTF-8 `.notes.md`.

```markdown
# 编译原理  ·  第一章习题

## 1.1 高级程序设计语言有哪两种翻译方式？

两种翻译方式：{x:编译程序|编译方式}和 **解释方式**。

1. **编译方式**：把源程序翻译成目标程序，再执行目标程序。
> 特点：翻译与执行分开；一次编译可多次运行。

2. **解释方式**：解释执行源程序，不生成独立目标程序。
> 特点：每次运行都要重新解释；便于{x:调式|调试}。
```

## Blocks

| Line | Meaning |
|---|---|
| `# …` | Page title (once, top) |
| `## 1.2 题干` | Heading. Leading `d.d` is drawn in red; the rest in navy |
| blank line | Small gap |
| ordinary paragraph | Body, wraps CJK |
| `> …` | Smaller, softer ink (特点 / 注释) |
| `- …` | Indented bullet (the `-` is not drawn) |

## Inline

| Token | Meaning |
|---|---|
| `**bold**` | Same handwriting font, heavier face if the TTC has one |
| `{x:错|对}` | Write 错, scribble/strike, write 对 on the same line |
| `{x:错\|对\|teal}` | Correction in teal (stage labels in 找错题) |

Do not put `{x:…}` on a line that is only `3.` — keep the correction inside the sentence.

## What not to put in the file

- “手写笔记·1.1-1.7”
- “第1页 / 全文手写体 / 手札体／翩翩体”
- Course answers you have not locked against the user or the slides
