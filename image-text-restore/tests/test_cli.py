from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SINGLE = ROOT / "scripts" / "enhance_raster.py"
BATCH = ROOT / "scripts" / "enhance_batch.py"


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments], capture_output=True, text=True, check=False
    )


class EnhanceCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_image(self, path: Path, size: tuple[int, int] = (16, 10)) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", size, (40, 90, 180)).save(path)

    def test_single_image_writes_and_verifies_expected_dimensions(self) -> None:
        source = self.root / "source.png"
        output = self.root / "output.png"
        self.make_image(source)

        completed = run(str(SINGLE), str(source), str(output), "--scale", "2")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "written")
        self.assertEqual(result["output_size"], [32, 20])
        with Image.open(output) as image:
            self.assertEqual(image.size, (32, 20))
            image.verify()

    def test_single_image_rejects_overwrite_and_aspect_distortion(self) -> None:
        source = self.root / "source.png"
        output = self.root / "output.png"
        self.make_image(source)
        output.write_bytes(b"occupied")

        overwrite = run(str(SINGLE), str(source), str(output), "--scale", "2")
        distortion = run(
            str(SINGLE), str(source), str(self.root / "square.png"),
            "--target", "32x32", "--dry-run",
        )

        self.assertNotEqual(overwrite.returncode, 0)
        self.assertIn("output exists", overwrite.stderr)
        self.assertNotEqual(distortion.returncode, 0)
        self.assertIn("aspect ratio", distortion.stderr)

    def test_batch_manifest_distinguishes_verified_and_failed_runs(self) -> None:
        inputs = self.root / "inputs"
        outputs = self.root / "outputs"
        self.make_image(inputs / "one.png")
        self.make_image(inputs / "two.jpg")

        first = run(str(BATCH), str(inputs), str(outputs), "--scale", "1")
        self.assertEqual(first.returncode, 0, first.stderr)
        manifest = json.loads((outputs / "manifest.json").read_text())
        self.assertEqual(manifest["expected_count"], 2)
        self.assertEqual(manifest["successful_count"], 2)
        self.assertEqual(manifest["failed_count"], 0)
        self.assertTrue(manifest["complete"])
        for item in manifest["items"]:
            self.assertEqual(item["status"], "verified")
            self.assertEqual(len(item["input_sha256"]), 64)
            self.assertEqual(len(item["output_sha256"]), 64)

        second = run(str(BATCH), str(inputs), str(outputs), "--scale", "1")
        self.assertNotEqual(second.returncode, 0)
        manifest = json.loads((outputs / "manifest.json").read_text())
        self.assertEqual(manifest["successful_count"], 0)
        self.assertEqual(manifest["failed_count"], 2)
        self.assertFalse(manifest["complete"])

    def test_batch_dry_run_is_planned_but_not_complete(self) -> None:
        inputs = self.root / "inputs"
        outputs = self.root / "outputs"
        self.make_image(inputs / "one.png")

        completed = run(
            str(BATCH), str(inputs), str(outputs), "--scale", "2", "--dry-run"
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        manifest = json.loads(completed.stdout)
        self.assertEqual(manifest["planned_count"], 1)
        self.assertEqual(manifest["successful_count"], 0)
        self.assertEqual(manifest["failed_count"], 0)
        self.assertFalse(manifest["complete"])
        self.assertFalse(outputs.exists())


if __name__ == "__main__":
    unittest.main()
