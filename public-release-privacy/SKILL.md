---
name: public-release-privacy
description: Audit a repository or release bundle before public publication, fail closed on privacy and secret risks, and report only finding categories and locations without echoing sensitive values. Use for public-repo cleanup, release review, or strict de-identification; not as a replacement for provider-side secret revocation or git-history rewriting.
---

# Public Release Privacy

Treat a clean working-tree scan as a release gate, not as proof that previously
published history is clean. Never print a matched token, address, URL, email,
archive member body, or symlink target.

## Workflow

1. Establish the release boundary. Prefer a clean checkout of the exact commit
   being published. Do not copy material from a private or dirty checkout.
2. Run `python3 scripts/scan_public_release.py PATH`. A nonzero result blocks
   publication. Findings contain only a category and a repository-relative
   location.
3. Remove or generalize the source material. Do not replace a secret with a
   reversible encoding or move it into an archive, Office file, fixture, hidden
   directory, or symlink.
4. Regenerate derived files, rerun project tests, rerun this scanner, and inspect
   the staged diff before publication.
5. If sensitive content was ever pushed, read
   [history-response.md](references/history-response.md). Scanning the current
   tree does not erase git history, forks, caches, logs, or released artifacts.

## Hard constraints

- Fail closed on unreadable files, malformed archives, encrypted ZIP members,
  archive byte/member-count limits, broken links, and links that escape the scan root.
- Treat absolute home paths, private collaboration links, credentials, email
  addresses, private-network endpoints, and sensitive filenames as blocking.
- Inspect member names and textual members inside ZIP, Office Open XML, TAR, and
  single-stream gzip archives, plus printable metadata in other binary files.
  Nested supported archives are scanned recursively within bounded depth and size
  limits. Sensitive locator components are replaced by stable hashes before output.
- Do not add real sensitive samples to tests. Construct synthetic fixtures at
  runtime from harmless fragments.
- Keep an explicit human review for names, prose, images, PDFs, and domain-specific
  identifiers that pattern matching cannot classify reliably.
