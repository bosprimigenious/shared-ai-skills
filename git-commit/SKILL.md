---
name: git-commit
description: Generate descriptive commit messages by analyzing git diffs. Use when writing commit messages, reviewing staged changes, or when the user asks for help with commits.
when-to-use: commit, git commit, commit message, staged, 提交, 写提交说明, 提交信息
---

# Git Commit Message Generator

## Instructions

1. Run `git diff --cached` to get staged changes
2. Analyze the diff to understand what changed
3. Generate a commit message following Conventional Commits format

## Format

```
<type>(<scope>): <short summary>

<body>
```

Types: feat, fix, refactor, docs, test, chore, perf, style

## Rules

- Summary: max 50 chars, imperative mood, no period at end
- Body: explain WHY, not WHAT (the diff shows what)
- If multiple logical changes, suggest splitting into separate commits

## Examples

Input: Added JWT authentication middleware
```
feat(auth): implement JWT-based authentication

Add middleware for token validation on protected routes
```

Input: Fixed null pointer in user service
```
fix(users): handle null response from auth provider

Prevent crash when external auth service returns empty response
```
