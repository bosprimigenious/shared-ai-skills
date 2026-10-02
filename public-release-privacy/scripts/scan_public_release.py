#!/usr/bin/env python3
"""Fail-closed privacy scanner that never echoes matched values."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tarfile
import zipfile

MAX_MEMBER = 16 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_FILE = 256 * 1024 * 1024
MAX_DEPTH = 3
MAX_MEMBERS = 10_000
TEXT_LIMIT = 16 * 1024 * 1024


def _joined(*parts: str) -> str:
    return "".join(parts)


COLLAB_HOSTS = tuple(
    _joined(*parts)
    for parts in (
        ("lark", "office.com"),
        ("feishu", ".cn"),
        ("feishu", ".com"),
    )
)

COLLAB_PATHS = tuple(
    _joined(*parts)
    for parts in (
        ("docs.google.com/", "document/d/"),
        ("drive.google.com/", "file/d/"),
        ("slack.com/", "archives/"),
        ("teams.microsoft.com/", "l/message/"),
        ("figma.com/", "file/"),
        ("figma.com/", "design/"),
        ("notion.so/",),
        ("sharepoint.com/",),
    )
)

PATTERNS = (
    ("absolute-home-path", re.compile(r"(?:/Users/|/home/)[A-Za-z0-9._-]+(?:/|\b)|[A-Za-z]:\\Users\\[^\\\s]+", re.I)),
    ("private-collaboration-link", re.compile(r"https?://[^\s<>'\"]*(?:" + "|".join(re.escape(h) for h in COLLAB_HOSTS) + r")[^\s<>'\"]*", re.I)),
    ("private-collaboration-link", re.compile(r"https?://[^\s<>'\"]*(?:" + "|".join(re.escape(p) for p in COLLAB_PATHS) + r")[^\s<>'\"]*", re.I)),
    ("email-address", re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I)),
    ("private-ip-endpoint", re.compile(r"(?<![0-9])(?:10(?:\.[0-9]{1,3}){3}|192\.168(?:\.[0-9]{1,3}){2}|172\.(?:1[6-9]|2[0-9]|3[01])(?:\.[0-9]{1,3}){2})(?::[0-9]{1,5})?(?![0-9])")),
    ("loopback-endpoint", re.compile(r"(?<![0-9])127(?:\.[0-9]{1,3}){3}(?::[0-9]{1,5})?(?![0-9])|\blocalhost:[0-9]{2,5}\b", re.I)),
    ("pem-private-key", re.compile(_joined("-----BEGIN ", "(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"))),
    ("github-token", re.compile(_joined("gh", r"[pousr]_[A-Za-z0-9]{20,}"))),
    ("aws-access-key", re.compile(_joined("AK", r"IA[0-9A-Z]{16}"))),
    ("service-api-key", re.compile(r"\b(?:sk|rk|pk)-[A-Za-z0-9_-]{20,}\b")),
    ("credential-assignment", re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9+/._-]{8,}")),
)

SENSITIVE_NAMES = (
    re.compile(r"^(?:\.env(?:\..+)?|\.netrc|\.npmrc|\.pypirc|\.git-credentials|kubeconfig|id_(?:rsa|dsa|ecdsa|ed25519)(?:\.pub)?|credentials?(?:\..+)?|secrets?(?:\..+)?|.*\.(?:pem|p12|pfx|jks|keystore))$", re.I),
    re.compile(r"(?:^|[-_.])(?:confidential|personal|private|internal)(?:[-_.]|$)", re.I),
)

TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".conf", ".xml", ".html", ".htm", ".csv", ".tsv", ".py",
    ".js", ".ts", ".tsx", ".jsx", ".sh", ".zsh", ".bash", ".fish", ".sql",
    ".tex", ".typ", ".rst", ".properties", ".gradle", ".java", ".go", ".rs",
}
ZIP_SUFFIXES = {".zip", ".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"}
TAR_SUFFIXES = {".tar", ".tgz", ".tbz", ".tbz2", ".txz"}


class Scanner:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.findings: set[tuple[str, str]] = set()

    @staticmethod
    def _opaque(value: str, label: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:12]
        return f"<{label}@{digest}>"

    def safe_location(self, location: str) -> str:
        """Keep a useful locator without reflecting sensitive path/member text."""
        line = ""
        match = re.search(r":([0-9]+)$", location)
        if match:
            line = match.group(0)
            location = location[: match.start()]
        if "!/" in location:
            outer, member = location.split("!/", 1)
            safe_outer = self.safe_location(outer)
            if re.fullmatch(r"<member@[0-9a-f]{12}>", member):
                safe_member = member
            else:
                safe_member = self._opaque(member, "member")
            return f"{safe_outer}!/{safe_member}{line}"

        safe_parts = []
        for part in PurePosixPath(location.replace("\\", "/")).parts:
            sensitive = any(pattern.search(part) for pattern in SENSITIVE_NAMES)
            sensitive = sensitive or any(pattern.search(part) for _, pattern in PATTERNS)
            safe_parts.append(self._opaque(part, "path") if sensitive else part)
        return "/".join(safe_parts) + line

    def add(self, kind: str, location: str) -> None:
        self.findings.add((kind, self.safe_location(location)))

    def check_name(self, name: str, location: str) -> None:
        normalized = name.replace("\\", "/")
        path = PurePosixPath(normalized)
        if path.is_absolute() or ".." in path.parts:
            self.add("unsafe-archive-path", location)
        base = path.name
        if any(pattern.search(normalized) for _, pattern in PATTERNS):
            self.add("sensitive-path", location)
        if any(pattern.search(base) for pattern in SENSITIVE_NAMES):
            self.add("sensitive-filename", location)

    def scan_text(self, data: bytes, location: str) -> None:
        if len(data) > TEXT_LIMIT:
            self.add("text-size-limit", location)
            return
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = data.decode("utf-16")
            except UnicodeDecodeError:
                self.add("undecodable-text", location)
                return
        for line_no, line in enumerate(text.splitlines(), 1):
            for kind, pattern in PATTERNS:
                if pattern.search(line):
                    self.add(kind, f"{location}:{line_no}")

    def scan_binary_strings(self, data: bytes, location: str) -> None:
        """Inspect printable metadata without reflecting or inventing decoded text."""
        if len(data) > TEXT_LIMIT:
            self.add("binary-size-limit", location)
            return
        text = data.decode("latin-1")
        for match in re.finditer(r"[\x20-\x7e]{8,}", text):
            fragment = match.group(0)
            for kind, pattern in PATTERNS:
                if pattern.search(fragment):
                    self.add(kind, location)

    def scan_blob(self, data: bytes, location: str, suffix: str, depth: int) -> None:
        suffix = suffix.lower()
        if depth > MAX_DEPTH:
            self.add("archive-depth-limit", location)
            return
        if suffix in ZIP_SUFFIXES:
            self.scan_zip(data, location, depth)
        elif suffix in TAR_SUFFIXES or location.lower().endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
            self.scan_tar(data, location, depth)
        elif suffix == ".gz":
            try:
                expanded = gzip.decompress(data)
            except (OSError, EOFError):
                self.add("malformed-archive", location)
                return
            if len(expanded) > MAX_MEMBER:
                self.add("archive-size-limit", location)
                return
            inner = location[:-3]
            self.scan_blob(expanded, inner, Path(inner).suffix, depth + 1)
        elif suffix in TEXT_SUFFIXES or suffix == "":
            self.scan_text(data, location)
        else:
            self.scan_binary_strings(data, location)

    def scan_zip(self, data: bytes, location: str, depth: int) -> None:
        total = 0
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                bad = archive.testzip()
                if bad is not None:
                    self.add("corrupt-archive-member", f"{location}!/{bad}")
                for member_count, item in enumerate(archive.infolist(), 1):
                    if member_count > MAX_MEMBERS:
                        self.add("archive-member-count-limit", location)
                        break
                    member = item.filename
                    member_loc = f"{location}!/{member}"
                    self.check_name(member, member_loc)
                    if item.flag_bits & 1:
                        self.add("encrypted-archive-member", member_loc)
                        continue
                    unix_mode = (item.external_attr >> 16) & 0xFFFF
                    if stat.S_ISLNK(unix_mode):
                        self.add("archive-link", member_loc)
                        continue
                    total += item.file_size
                    if item.file_size > MAX_MEMBER or total > MAX_TOTAL:
                        self.add("archive-size-limit", member_loc)
                        continue
                    if item.is_dir():
                        continue
                    payload = archive.read(item)
                    self.scan_blob(payload, member_loc, Path(member).suffix, depth + 1)
        except (OSError, RuntimeError, zipfile.BadZipFile, NotImplementedError):
            self.add("malformed-archive", location)

    def scan_tar(self, data: bytes, location: str, depth: int) -> None:
        total = 0
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                for member_count, item in enumerate(archive, 1):
                    if member_count > MAX_MEMBERS:
                        self.add("archive-member-count-limit", location)
                        break
                    member_loc = f"{location}!/{item.name}"
                    self.check_name(item.name, member_loc)
                    if item.issym() or item.islnk():
                        self.add("archive-link", member_loc)
                        continue
                    if not item.isfile():
                        continue
                    total += item.size
                    if item.size > MAX_MEMBER or total > MAX_TOTAL:
                        self.add("archive-size-limit", member_loc)
                        continue
                    stream = archive.extractfile(item)
                    if stream is None:
                        self.add("unreadable-archive-member", member_loc)
                        continue
                    self.scan_blob(stream.read(), member_loc, Path(item.name).suffix, depth + 1)
        except (OSError, EOFError, tarfile.TarError):
            self.add("malformed-archive", location)

    def scan_file(self, path: Path) -> None:
        location = path.relative_to(self.root).as_posix()
        self.check_name(path.name, location)
        try:
            if path.stat().st_size > MAX_FILE:
                self.add("file-size-limit", location)
                return
            data = path.read_bytes()
        except OSError:
            self.add("unreadable-file", location)
            return
        self.scan_blob(data, location, path.suffix, 0)

    def run(self) -> list[tuple[str, str]]:
        if not self.root.is_dir():
            self.add("invalid-scan-root", ".")
            return sorted(self.findings)
        for base, dirs, files in os.walk(self.root, topdown=True, followlinks=False):
            base_path = Path(base)
            dirs[:] = sorted(d for d in dirs if d != ".git")
            files.sort()
            for name in list(dirs):
                path = base_path / name
                if path.is_symlink():
                    self.add("symlink", path.relative_to(self.root).as_posix())
                    dirs.remove(name)
            for name in files:
                path = base_path / name
                location = path.relative_to(self.root).as_posix()
                if location == ".git":
                    continue
                try:
                    mode = path.lstat().st_mode
                except OSError:
                    self.add("unreadable-file", location)
                    continue
                if stat.S_ISLNK(mode):
                    self.add("symlink", location)
                elif stat.S_ISREG(mode):
                    self.scan_file(path)
                else:
                    self.add("unsupported-file-type", location)
        return sorted(self.findings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a public-release tree without echoing matched values")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    findings = Scanner(Path(args.path)).run()
    if args.json:
        print(json.dumps([{"category": kind, "location": loc} for kind, loc in findings], indent=2))
    else:
        for kind, loc in findings:
            print(f"FAIL {kind} {loc}")
        print(f"privacy findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
