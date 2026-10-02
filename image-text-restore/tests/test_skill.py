from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_frontmatter_and_document_links(self) -> None:
        skill = (ROOT / "SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\n"))
        _, frontmatter, _ = skill.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        self.assertEqual(metadata["name"], "image-text-restore")
        self.assertEqual(metadata["license"], "MIT")

        for relative in (
            "references/prompts.md",
            "references/generation-stage.md",
            "references/image-enhancement.md",
            "references/diagram-restoration.md",
            "scripts/enhance_raster.py",
            "scripts/enhance_batch.py",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
