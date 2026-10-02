# Previously published sensitive material

If a secret or private identifier reached a remote repository, a clean new commit
is not remediation by itself.

1. Revoke or rotate credentials first. Assume cloning, logs, caches, and forks
   preserved the exposed value.
2. Record the affected paths, commits, releases, and artifacts in a private
   incident log. Do not paste the value into an issue or commit message.
3. Create a recoverable mirror backup, then use the hosting provider's documented
   history-removal procedure. Coordinate force-pushes because they invalidate
   existing clones and open work.
4. Delete or replace affected release assets and caches where the platform allows.
5. Scan a fresh clone of every rewritten ref and verify that collaborators have
   discarded contaminated clones.

Do not rewrite history automatically from this skill. That operation needs an
explicit target list, a rollback snapshot, and user authorization.
