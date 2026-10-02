# AI Image Enhancement

Use this reference for generated illustrations, rendered artwork, photographs, and other raster images whose main problem is blur, compression, noise, or insufficient output size.

## Choose the Route

Start with the cheapest route that can satisfy the request:

1. **Deterministic baseline** for correct images that are merely soft or small. Resize with a high-quality filter, apply restrained sharpening, and compare with the source.
2. **Local generative repair** when a specific face, hand, texture, edge, or object is malformed. Mask only that region and preserve the rest of the image.
3. **Neural super-resolution** when conventional enlargement remains visibly soft. Keep a deterministic candidate because the model may invent texture.
4. **Reconstruction** for text-heavy diagrams, screenshots, tables, or layouts. Read `diagram-restoration.md`.

Do not run every method in sequence by default. Each additional generative pass raises the chance of identity, geometry, text, or style drift.

## Prompt Contract for Local Repair

State the invariant before the desired improvement:

```text
Use the input as the composition and identity reference. Keep the canvas ratio, crop,
camera/viewpoint, subject identity, pose, object count, object positions, palette, and
overall art direction unchanged. Repair only [precise region and defect]. Improve its
edge definition, coherent texture, and local detail so it matches the surrounding
image. Do not add text, objects, decorations, limbs, logos, or symbols.
```

For an image containing text, use the stricter prompt variants in `prompts.md` and verify the text separately.

## What “Clearer” Can Mean

- **Larger dimensions**: more pixels, without proof of new information.
- **Higher acutance**: edges look sharper; too much creates halos.
- **Lower noise/compression**: flat regions look cleaner; too much removes texture.
- **Recovered detail**: plausible new texture from a model; it may not be true to the source.
- **Better readability**: text or small structure is easier to interpret; this may require reconstruction rather than upscaling.

Name the achieved property precisely in the result report.

## Visual Acceptance

Inspect the source and candidate at fit view, 100%, and 200%. Check representative crops containing:

- the main subject or focal object;
- fine repeated texture such as hair, fabric, foliage, or architecture;
- high-contrast edges against flat backgrounds;
- faces, hands, logos, symbols, and any text;
- gradients and flat fills where tile seams or banding are visible.

Reject candidates with doubled edges, ringing halos, plastic skin, waxy texture, invented micro-detail, changed identity, extra objects, distorted anatomy, altered text, block seams, or composition drift.

## Reporting

Report input and output dimensions, method, output path, and inspected regions. Describe model-created detail as reconstructed or enhanced, not recovered fact. For batch work, report the verified output count against the expected input count.
