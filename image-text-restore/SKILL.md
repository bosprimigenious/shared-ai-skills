---
name: image-text-restore
description: Generate clear AI images and restore or upscale existing raster images while preserving structure and text accuracy. Use for GPT Image 2 or 2.5 generation-quality planning, high-resolution image generation, post-generation sharpening, safe enlargement, local detail repair, garbled or blurry text, and delivery of posters, diagrams, screenshots, infographics, menus, labels, covers, and UI images. Prefer imagegen for creative restyling without fidelity constraints.
license: MIT
metadata:
  when-to-use: "GPT Image 2, GPT Image 2.5, AI生图清晰, 高清生图, AI图片变清晰, 图片高清放大, 锐化, 修图中文, 文字糊, 错字, 海报修字, 架构图重绘, 矢量文字, 截图清晰, 菜单文字, 放大图片保字"
---

# Image Text Restore

Use this skill during image generation and after an image already exists. Treat Chinese text as content, not decoration. Separate five different goals before choosing a method: a clean initial render, more pixels, sharper appearance, correct text, and enough layout space. They require different controls and repairs.

For ordinary AI-generated illustrations without important text, use the same evidence-first approach but skip OCR and typography reconstruction. Preserve the original composition unless the user asks for a redesign.

## Two-Stage Clarity Model

Classify the request before acting:

1. **Generation-time clarity**: set an explicit model, native output size, quality level, aspect ratio, output format, and composition constraints before generating. Produce inexpensive candidates first when practical, then render the selected composition at the highest useful native quality. This is the preferred route for GPT Image 2, GPT Image 2.5, and other generators that expose size and quality controls.
2. **Post-generation clarity**: inspect the existing image, preserve an immutable original, then choose deterministic enlargement and sharpening, neural super-resolution, masked generative repair, typography reconstruction, or vector rebuilding.

Do not describe these stages as interchangeable. A larger canvas does not repair malformed anatomy or wrong text, sharpening does not add reliable missing information, and a generative upscaler may change content while making it look more detailed.

Read [references/generation-stage.md](references/generation-stage.md) before generating a new image whose clarity, final dimensions, text, or print/display use matters.

## Core Rule

Do not rely on an image model as the final source of Chinese text. Use image generation/editing for background, layout, texture, lighting, edges, and local detail. Use OCR, human-readable transcription, or user-provided text as the source of truth, then re-render important text with real fonts or ask for explicit confirmation before finalizing.

## Default Workflow

If the image does not exist yet, run the generation-stage workflow first. Once a candidate exists, continue with the inventory and post-generation steps below only when the native render still misses the delivery target.

1. Inventory the source image.
   - Record file path, dimensions, format, and visible content.
   - Identify whether it is a typography poster, diagram, screenshot, document, UI, or photo with labels.
   - Mark text-heavy areas and non-text detail areas.

2. Build a text source of truth.
   - OCR the image when OCR tooling is available.
   - If OCR is unreliable, visually transcribe the important text.
   - Ask the user for exact text only when the text is too small, ambiguous, or legally/technically important.
   - Create a short correction table: location, current/uncertain text, correct text.

3. Diagnose the actual failure and choose the least generative route that can fix it.
   - **Readable text, soft pixels**: preserve the raster and use deterministic denoise, local contrast, resampling, and restrained sharpening. Do not regenerate readable text.
   - **A few wrong or blurry labels**: clear each complete old text box, including antialiasing and shadow, then render verified text with a real font.
   - **Dense diagram with correct geometry**: reconstruct editable text and shapes in SVG/HTML/canvas/PDF. Use source-coordinate transforms and preserve an editable intermediate.
   - **Text cannot be separated from the background**: create a genuinely text-free base, then add verified vector text. Compare the base against the source because model-based text removal can move icons, boxes, and arrows.
   - **Layout is crowded**: reflow the layout from measured text bounds. More pixels at the same geometry do not create more room inside boxes. Reject any render where a glyph or line box crosses its container.
   - **Art poster with large title text**: use GPT Image 2 for local visual refinement, but render the final title with a real font or verified typography layer.
   - **Background/detail only**: mask/protect text and repaint only non-text regions.

4. Upscale in stages.
   - Keep the original immutable and create named candidates in a separate output directory.
   - Start with deterministic or conventional scaling when possible to create a large working canvas.
   - Use model-based editing for local detail only after text regions are protected, blanked, or separately planned.
   - Use Real-ESRGAN, Upscayl, or similar super-resolution only after content and layout are correct. They may invent detail and cannot fix incorrect text or crowded boxes.
   - Avoid extreme enlargement in one pass. When the target is 7680x4320, a controlled 3840x2160 input followed by 2x super-resolution can be more practical than enlarging an existing 8K raster to 16K or 32K.
   - Avoid asking the model to “make all Chinese clear” without a text source of truth; it may invent strokes or substitute characters.

5. Re-render or verify text.
   - Use reliable Chinese fonts such as Source Han Sans, Source Han Serif, PingFang SC, Noto Sans CJK, or an existing project font.
   - Resolve and record the actual font used. If a preferred font is unavailable, keep the intended size instead of silently switching to a fallback with a smaller size, then remeasure every affected text box.
   - Match original alignment, weight, spacing, color, shadows, outlines, and perspective as much as the task requires.
   - Keep text editable until final export if practical.
   - Compare every important character against the correction table.
   - Clear the full old glyph bounds before drawing new text. Directly overlaying a different font commonly creates doubled strokes because font width, baseline, line height, and antialiasing differ.
   - Draw multiline text as explicit lines or SVG `tspan` elements. Do not assume HTML `<br>` will survive an HTML-to-SVG or SVG-to-raster pipeline.
   - Keep one coordinate system. If the reference and output sizes differ, record `scale_x` and `scale_y` and apply them to boxes, font sizes, strokes, and padding. On macOS, distinguish image point size/DPI from actual pixel dimensions.

6. Export and inspect.
   - Export at the requested large resolution; use 2x/4x/8K-style output when appropriate.
   - Visually inspect at 100% zoom and a fit-to-screen view.
   - Verify that text is readable, no new garbled Chinese appears, and local repainting did not change factual content.
   - Inspect representative crops at 100% and 200%, not only a fit-to-screen preview.
   - Check for ghost text, white repair rectangles, sharpening halos, clipped glyphs, overlaps, and shifted icons/arrows.
   - Label intermediate outputs as `draft`, `candidate`, or `blank-base`. Do not call a set final merely because every file has the requested dimensions.
   - For a batch, compare the expected input manifest with successfully decoded outputs one by one. A script exit code or final `Done` line is not evidence that every image was produced.

## Deterministic Baseline

When Pillow is available, use `scripts/enhance_raster.py` before a generative edit if conventional scaling and restrained sharpening may be sufficient. It never overwrites an existing file unless `--force` is supplied, supports a dry run, limits accidental giant outputs, rejects unintended aspect-ratio distortion, and prints a JSON result for verification.

```bash
python3 scripts/enhance_raster.py input.png output.png --scale 2 --mode illustration
python3 scripts/enhance_raster.py input.png output.png --target 3840x2160 --mode text --dry-run
python3 scripts/enhance_batch.py inputs/ outputs/ --scale 2 --mode illustration
```

Modes are decision hints rather than guarantees:

- `text`: restrained sharpening and no contrast change;
- `illustration`: mild contrast and edge enhancement for generated art;
- `photo`: conservative photographic sharpening.

This baseline cannot reconstruct detail that is absent from the source. If it does not meet the target, preserve it as a comparison candidate and proceed to local model-based repair or an external super-resolution tool.

For more than one input, use `scripts/enhance_batch.py`. It accepts PNG, JPEG, and WebP files, invokes the single-image command for each item, and writes `manifest.json` with expected, successful, and failed counts plus input/output hashes. Treat a nonzero exit or any failed manifest item as an incomplete batch.

## Iterative Calibration Loop

For vector reconstruction or text replacement, iterate on small regions instead of rendering the whole image blindly:

1. Render the editable source at the target pixel dimensions.
2. Crop a text-dense region and a structure-dense region.
3. Compare them with the reference at the same scale.
4. Correct text boxes, baselines, wrapping, font metrics, and any moved structure.
5. Repeat until the crops pass, then inspect the whole image.

OCR provides draft boxes and transcription, not final truth. Correct OCR before rendering. If OCR is unavailable or unreliable, use a known-good reference or a user-provided transcription; do not fabricate unreadable labels.
An OCR command that runs but returns zero observations or an error is unavailable evidence, not an empty transcription.

## GPT Image 2 Editing Prompt Template

Use this style when editing with an image model:

```text
Use the input image as the exact layout and composition reference. Improve local detail, edge clarity, texture, lighting, and overall sharpness. Preserve the original structure, positions, colors, and proportions.

Critical text rule: do not invent, rewrite, translate, or modify any Chinese text. Do not create new text. Leave text regions unchanged or cleanly blank if requested. Any final Chinese text will be re-rendered separately from an exact text source of truth.

Focus only on non-text visual detail and background restoration. Avoid hallucinated symbols, pseudo-Chinese, extra labels, or decorative strokes that resemble text.
```

For local inpainting, add:

```text
Only repaint the masked/selected area. Blend it with the surrounding style. Keep all unmasked areas pixel/layout consistent. If the selected area contains text, remove/blank it cleanly rather than redrawing text.
```

For a new GPT Image 2 or 2.5 generation, use the generation contract and parameter checklist in `references/generation-stage.md`. Specify real API/tool controls such as size and quality when available; prompt adjectives such as “4K,” “8K,” or “ultra detailed” are not evidence that the requested pixel dimensions or rendering quality were used.

## Text Correction Table

Use a compact table before final rendering:

```markdown
| Area | Current/OCR Text | Correct Text | Confidence | Action |
| --- | --- | --- | --- | --- |
| Main title | ... | ... | high/medium/low | re-render / preserve / ask user |
```

## Quality Checks

Before final response, check:

- Important Chinese text is sourced from OCR/transcription/user text, not model guesswork.
- No pseudo-Chinese, broken radicals, missing strokes, extra strokes, or wrong characters remain in final text areas.
- Text is sharp at 100% zoom and readable at target display size.
- Local repainting improved detail without changing diagrams, arrows, labels, icons, or factual relationships.
- Output dimensions and file paths are reported.
- For new generations, the selected model, requested native dimensions, quality setting, and output format are reported when the tool exposes them.
- Pixel dimensions increased only when that serves the delivery target; dimension alone is not claimed as evidence of recovered detail.
- Text boxes have enough room at the intended viewing size; no label depends on zooming far beyond normal use just to become legible.
- The chosen route and its limitation are stated: deterministic enhancement preserves content but cannot recover missing strokes; model-based enhancement can invent detail; vector reconstruction can change layout if coordinates are not calibrated.

## When To Prefer Rebuilding

For architecture diagrams, UI screenshots, tables, slides, and text-dense infographics, rebuilding the image as editable SVG/HTML/PPTX/vector layers is usually more accurate than image-only enhancement. Use the original image as a visual reference, reconstruct boxes/arrows/text with real text, then export a high-resolution PNG/PDF.

Read [references/diagram-restoration.md](references/diagram-restoration.md) before repairing a dense diagram, rebuilding text layers, removing all text to form a base, or using super-resolution on an 8K target.

## References

Read `references/prompts.md` when you need ready-made prompt variants for enhancement, background-only repainting, typography poster repair, or diagram restoration.

Read [references/image-enhancement.md](references/image-enhancement.md) for ordinary AI-generated illustrations, photographs, and choosing between deterministic scaling, local generative repair, and neural super-resolution.

Read [references/generation-stage.md](references/generation-stage.md) for GPT Image 2/2.5 and other model-generation workflows that need native clarity before post-processing.
