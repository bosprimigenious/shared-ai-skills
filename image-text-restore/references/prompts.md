# Prompt Variants

## New high-clarity generation

```text
Create a clean native-resolution image for the requested delivery size and aspect ratio.
Use coherent fine detail, well-defined silhouettes, clean material boundaries, natural
local contrast, and controlled texture. Preserve the requested subject count, identity,
pose, camera/viewpoint, geometry, and palette. Avoid haze, muddy edges, oversharpening
halos, duplicated anatomy, pseudo-text, watermarks, and unrequested symbols. Keep the
specified text area clean and visually quiet for later typesetting.
```

Set model, size, quality, format, and compression through the image tool or API. Prompt words such as `4K` or `8K` do not replace those controls.

## Background-only detail enhancement

```text
Enhance only the non-text visual areas of this image. Increase apparent resolution, sharpen edges, restore fine texture, reduce blur/noise, and improve local contrast. Preserve composition, layout, colors, arrows, icons, and all object positions. Do not generate, modify, or add Chinese text. Protect text areas from change.
```

## Blank text for later re-rendering

```text
Cleanly remove the selected garbled or blurry text while preserving the surrounding material, lighting, perspective, background texture, and layout. Do not replace it with new text. Leave a natural blank area suitable for adding exact typography later.
```

## Typography poster repair

```text
Use the image as a composition reference. Improve the background, material quality, lighting, edges, and local details to a premium typography-poster finish. Keep the central text area reserved and do not invent Chinese characters. The final title text will be typeset separately from exact characters.
```

## Diagram restoration

```text
Restore line clarity, icon edges, color separation, and background cleanliness while preserving the diagram exactly. Do not change arrows, boxes, relationships, labels, numbering, or any Chinese/English text. If a text region is unclear, leave it unchanged for manual re-rendering instead of guessing.
```

## Final text rendering instruction

```text
Typeset the following exact text, character-for-character, using a real Chinese font. Match the original placement, size, color, alignment, and visual hierarchy. Do not substitute simplified/traditional forms unless explicitly requested. Do not add decorative pseudo-strokes that change readability.
```
