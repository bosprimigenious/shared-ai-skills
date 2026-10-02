# Generation-Stage Clarity

Use this reference before generating an image when the final output must be clear, large, printable, text-safe, or suitable for later restoration. It applies to GPT Image 2, GPT Image 2.5, and other image generators with native size, quality, reference-image, or editing controls.

## Preflight Contract

Record these fields before the final generation:

- intended use: screen, social media, slide, poster, print, UI asset, or diagram;
- target aspect ratio and minimum pixel dimensions;
- generator and exact model identifier exposed by the current tool;
- native size and quality setting;
- output format and compression setting;
- elements that must remain invariant: identity, pose, camera, object count, geometry, palette, and empty text zones;
- areas allowed to change during local repair;
- whether text will be rendered separately with real fonts.

Provider capabilities change. Inspect the current tool schema or official provider documentation instead of guessing model names, supported dimensions, or quality values.

## GPT Image 2 and 2.5

For GPT Image 2 (also commonly described by users as Image 2.0) and GPT Image 2.5-family tools:

1. Select the exact image model rather than relying on an automatic model choice when the interface permits it.
2. Set the native `size` and `quality` controls explicitly. Use the final aspect ratio during generation so a later crop does not discard detail.
3. Use a lower-cost quality for composition candidates when appropriate. Generate the selected composition again at the highest useful native quality for the final asset.
4. For edit or reference-image workflows, request the highest available input fidelity and state the invariants in the prompt.
5. Prefer PNG or lossless WebP for text, diagrams, flat graphics, and further editing. Use high-quality JPEG only when file size or compatibility requires it.
6. Treat “4K,” “8K,” “sharp,” and “ultra detailed” inside the prompt as visual-direction words. Verify the returned pixel dimensions and actual tool parameters separately.

## Generation Contract

Put invariants before decorative detail:

```text
Create a clean native-resolution image for [delivery use] at [aspect ratio].
Keep [subject identity, object count, camera/viewpoint, pose, geometry, palette,
and reserved text areas] stable. Use coherent fine detail, well-defined silhouettes,
clean material boundaries, natural local contrast, and controlled texture. Avoid haze,
muddy edges, oversharpening halos, duplicated anatomy, pseudo-text, watermarks, and
unrequested symbols. Leave [text area] clean and visually quiet for later typesetting.
```

Add content and style requirements after this contract. Supply exact size, quality, and format through tool parameters when they exist.

## Candidate-to-Final Loop

1. Generate multiple candidates at an economical quality.
2. Reject candidates with incorrect composition, anatomy, identity, geometry, or text-like artifacts before spending on high quality.
3. Select one composition and generate or edit it at the highest useful native size and quality.
4. Inspect the native result at fit view, 100%, and 200%.
5. Repair isolated defects with a tight mask. Keep unmasked regions invariant.
6. Render exact text separately when typography matters.
7. Run deterministic or neural enlargement only if the native output is still smaller or softer than the delivery target.

Avoid repeated whole-image generative passes. Each pass can accumulate changes in identity, geometry, color, and text.

## Choosing the Post-Generation Route

- **Correct content, slightly soft**: use deterministic Lanczos enlargement and restrained sharpening.
- **Correct content, insufficient texture**: compare a conservative neural super-resolution candidate with the deterministic baseline.
- **One malformed region**: use masked generative repair, then compare outside the mask against the selected native render.
- **Creative artwork where new texture is acceptable**: use a creative upscaler and label its new detail as generated.
- **Identity, product, scientific, architectural, or diagram content**: default to the most faithful route and reject semantic changes.
- **Text-heavy output**: generate a clean background and reconstruct the text or diagram as editable layers.

## Acceptance Record

Report:

- exact model identifier when available;
- requested and decoded pixel dimensions;
- requested quality and output format;
- number of candidates and why the selected one passed;
- local repairs or upscaling applied afterward;
- inspected regions and rejected artifacts;
- whether any visible detail was generated rather than preserved from a source.
