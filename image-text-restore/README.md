# Image Text Restore

A Codex skill for generating clear AI images and making existing AI-generated or text-heavy images clearer without silently changing their content. It covers both native generation with GPT Image 2/2.5 and post-generation enlargement, sharpening, repair, and text reconstruction.

It separates five problems that are often confused:

- producing a clean native render;
- adding pixels;
- sharpening visible edges;
- correcting unreadable or malformed text;
- giving dense layouts enough room.

The skill chooses between deterministic enlargement, local generative repair, neural super-resolution, and editable vector reconstruction. It treats model-generated detail as a reconstruction rather than recovered fact.

## Install

Ask Codex:

```text
Use $skill-installer to install the skill from
https://github.com/bosprimigenious/image-text-restore-skill
```

Or clone it manually:

```bash
git clone https://github.com/bosprimigenious/image-text-restore-skill.git \
  ~/.codex/skills/image-text-restore
```

Restart Codex after installing a new skill.

## Use

For generation-time clarity with GPT Image 2, GPT Image 2.5, or another image model:

```text
Use $image-text-restore while generating this image. Set an explicit native size and
quality, preserve the requested composition, leave a clean area for real typography,
and verify the decoded pixel dimensions before any post-processing.
```

Attach or identify an image, then ask:

```text
Use $image-text-restore to enlarge this generated illustration to 4K. Preserve the
composition and identity, repair only malformed local details, and compare the result
with a deterministic upscale.
```

For images containing Chinese or dense text:

```text
Use $image-text-restore to make this diagram clearer. Keep every label exact, rebuild
unreadable text with real fonts, and verify the result at 100% zoom.
```

## Deterministic helper

The bundled helper uses Pillow for conventional Lanczos enlargement and restrained sharpening. It does not call an image model or invent missing detail.

```bash
python3 -m pip install Pillow
python3 scripts/enhance_raster.py input.png output.png --scale 2 --mode illustration
```

Available modes are `illustration`, `photo`, and `text`. Use `--dry-run` to inspect the output plan. Existing outputs, giant canvases, shrinking, and major aspect-ratio changes are rejected by default.

For a directory of images:

```bash
python3 scripts/enhance_batch.py inputs/ outputs/ --scale 2 --mode illustration
```

The batch command writes `outputs/manifest.json`. Each item includes source and output dimensions and SHA-256 hashes. The command fails if the input directory is empty, a candidate cannot be written and decoded, output names collide, or the verified output count differs from the expected count.

## Limits

- Enlarging dimensions alone cannot restore information absent from the source.
- Generative enhancement can invent texture, change identity, distort anatomy, or alter text.
- OCR is a draft transcription and must be checked for important text.
- Dense diagrams may require editable text and geometry rather than image-only enhancement.

See [SKILL.md](SKILL.md) for the workflow, [generation-stage.md](references/generation-stage.md) for GPT Image 2/2.5 and other native generation, [image-enhancement.md](references/image-enhancement.md) for post-generation artwork and photographs, and [diagram-restoration.md](references/diagram-restoration.md) for text-heavy layouts.

## License

MIT
