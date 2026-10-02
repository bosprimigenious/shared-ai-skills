from __future__ import annotations

import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile
from unittest import mock

import scan_public_release as scanner_module
from scan_public_release import Scanner


class ScannerTests(unittest.TestCase):
    def scan(self, files: dict[str, bytes | str]):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, data in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data.encode() if isinstance(data, str) else data)
            return Scanner(root).run()

    def categories(self, findings):
        return {kind for kind, _ in findings}

    def test_clean_tree_passes(self):
        self.assertEqual([], self.scan({"README.md": "portable public example\n"}))

    def test_secret_output_does_not_echo_value(self):
        token = "gh" + "p_" + "A" * 30
        findings = self.scan({"notes.txt": token})
        rendered = repr(findings)
        self.assertIn("github-token", self.categories(findings))
        self.assertNotIn(token, rendered)

    def test_home_collaboration_email_and_private_endpoint(self):
        text = "\n".join((
            "/" + "Users" + "/specific-person/project",
            "https://" + "example." + "lark" + "office.com/wiki/private",
            "person" + "@" + "real-domain.test",
            "10" + ".12.0.8:9000",
        ))
        cats = self.categories(self.scan({"notes.md": text}))
        self.assertTrue({"absolute-home-path", "private-collaboration-link", "email-address", "private-ip-endpoint"} <= cats)

    def test_sensitive_filename(self):
        filename = ".env.local"
        findings = self.scan({filename: "SAFE=x"})
        self.assertIn("sensitive-filename", self.categories(findings))
        self.assertNotIn(filename, repr(findings))
        self.assertIn("<path@", repr(findings))

    def test_zip_member_name_and_text_are_scanned(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            archive.writestr("credentials.txt", "/" + "home" + "/named-user/work")
        cats = self.categories(self.scan({"bundle.zip": buf.getvalue()}))
        self.assertTrue({"sensitive-filename", "absolute-home-path"} <= cats)

    def test_sensitive_archive_member_is_not_echoed(self):
        private_member = "person" + "@" + "real-domain.test"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            archive.writestr(private_member, "clean")
        rendered = repr(self.scan({"bundle.zip": buf.getvalue()}))
        self.assertNotIn(private_member, rendered)
        self.assertIn("<member@", rendered)

    def test_zip_traversal_and_link_are_blocking(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            archive.writestr("../outside.txt", "clean")
            link = zipfile.ZipInfo("shortcut")
            link.create_system = 3
            link.external_attr = 0o120777 << 16
            archive.writestr(link, "target")
        cats = self.categories(self.scan({"bundle.zip": buf.getvalue()}))
        self.assertTrue({"unsafe-archive-path", "archive-link"} <= cats)

    def test_office_xml_is_scanned(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            archive.writestr("word/document.xml", "person" + "@" + "company.test")
        self.assertIn("email-address", self.categories(self.scan({"report.docx": buf.getvalue()})))

    def test_binary_metadata_is_scanned(self):
        token = "gh" + "p_" + "B" * 30
        findings = self.scan({"asset.bin": b"\x00\xffmetadata=" + token.encode() + b"\x00"})
        self.assertIn("github-token", self.categories(findings))
        self.assertNotIn(token, repr(findings))

    def test_tar_member_is_scanned(self):
        buf = io.BytesIO()
        payload = ("password" + "=" + "not-a-real-value").encode()
        with tarfile.open(fileobj=buf, mode="w") as archive:
            info = tarfile.TarInfo("config.txt")
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
        self.assertIn("credential-assignment", self.categories(self.scan({"bundle.tar": buf.getvalue()})))

    def test_symlink_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.txt").write_text("clean")
            (root / "link.txt").symlink_to("target.txt")
            self.assertIn("symlink", self.categories(Scanner(root).run()))

    def test_malformed_archive_fails_closed(self):
        self.assertIn("malformed-archive", self.categories(self.scan({"bad.zip": b"not a zip"})))

    def test_zip_member_count_limit_fails_closed(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            for index in range(4):
                archive.writestr(f"item-{index}.txt", "")
        with mock.patch.object(scanner_module, "MAX_MEMBERS", 3):
            self.assertIn("archive-member-count-limit", self.categories(self.scan({"many.zip": buf.getvalue()})))

    def test_tar_member_count_limit_fails_closed(self):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as archive:
            for index in range(4):
                info = tarfile.TarInfo(f"item-{index}.txt")
                info.size = 0
                archive.addfile(info, io.BytesIO())
        with mock.patch.object(scanner_module, "MAX_MEMBERS", 3):
            self.assertIn("archive-member-count-limit", self.categories(self.scan({"many.tar": buf.getvalue()})))


if __name__ == "__main__":
    unittest.main()
