#!/usr/bin/env python3
"""Batch wrapper for enhance_raster.py with a verified output manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc

from enhance_raster import MODE_SETTINGS, parse_target


SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enhance a directory of raster images and verify every output."
    )
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    size = parser.add_mutually_exclusive_group(required=True)
    size.add_argument("--scale", type=float)
    size.add_argument("--target", type=parse_target)
    parser.add_argument("--mode", choices=MODE_SETTINGS, default="illustration")
    parser.add_argument(
        "--format",
        choices=("same", "png", "jpg", "webp"),
        default="same",
        help="output format (default: preserve each input extension)",
    )
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--allow-distortion", action="store_true")
    parser.add_argument("--max-megapixels", type=float, default=200.0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def output_suffix(source: Path, requested: str) -> str:
    if requested == "same":
        return source.suffix.lower()
    return ".jpg" if requested == "jpg" else f".{requested}"


def discover(root: Path, recursive: bool) -> list[Path]:
    iterator = root.rglob("*") if recursive else root.glob("*")
    return sorted(
        path for path in iterator if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=".manifest.",
        suffix=".json",
        dir=path.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    args = build_parser().parse_args()
    input_dir = args.input_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not input_dir.is_dir():
        raise SystemExit(f"input directory does not exist: {input_dir}")
    if input_dir == output_dir:
        raise SystemExit("input and output directories must be different")
    if args.recursive and input_dir in output_dir.parents:
        raise SystemExit("recursive output directory must not be inside the input directory")

    sources = discover(input_dir, args.recursive)
    if not sources:
        raise SystemExit(f"no supported images found in: {input_dir}")

    planned: list[tuple[Path, Path]] = []
    names: set[str] = set()
    for source in sources:
        relative = source.relative_to(input_dir)
        suffix = output_suffix(source, args.format)
        output = output_dir / relative.parent / f"{source.stem}{suffix}"
        collision_key = str(output).casefold()
        if collision_key in names:
            raise SystemExit(f"output name collision: {output}")
        names.add(collision_key)
        planned.append((source, output))

    items: list[dict[str, object]] = []
    enhancer = Path(__file__).with_name("enhance_raster.py")
    for source, output in planned:
        command = [
            sys.executable,
            str(enhancer),
            str(source),
            str(output),
            "--mode",
            args.mode,
            "--max-megapixels",
            str(args.max_megapixels),
        ]
        if args.scale is not None:
            command.extend(("--scale", str(args.scale)))
        else:
            command.extend(("--target", f"{args.target[0]}x{args.target[1]}"))
        if args.allow_distortion:
            command.append("--allow-distortion")
        if args.force:
            command.append("--force")
        if args.dry_run:
            command.append("--dry-run")

        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        item: dict[str, object] = {
            "input": str(source),
            "output": str(output),
            "status": "failed",
        }
        if completed.returncode == 0:
            try:
                result = json.loads(completed.stdout)
                item.update(result)
                item["input_sha256"] = sha256(source)
                if not args.dry_run:
                    with Image.open(output) as image:
                        image.verify()
                    item["output_sha256"] = sha256(output)
                    item["status"] = "verified"
                else:
                    item["status"] = "planned"
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                item["error"] = f"verification failed: {exc}"
        else:
            item["error"] = (completed.stderr or completed.stdout).strip()
        items.append(item)

    failed = sum(item["status"] == "failed" for item in items)
    planned_count = sum(item["status"] == "planned" for item in items)
    verified_count = sum(item["status"] == "verified" for item in items)
    manifest: dict[str, object] = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "expected_count": len(planned),
        "planned_count": planned_count,
        "successful_count": verified_count,
        "failed_count": failed,
        "complete": not args.dry_run and failed == 0 and verified_count == len(planned),
        "items": items,
    }

    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "manifest.json"
        write_manifest(manifest_path, manifest)
        print(json.dumps({**manifest, "manifest": str(manifest_path)}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
