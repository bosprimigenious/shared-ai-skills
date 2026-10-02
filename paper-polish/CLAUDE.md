# Paper Polish

> Turn experiment results and evidence ledgers into polished top-conference paper prose, and iterate on a manuscript without overclaiming. Use when writing or rewriting an abstract, introduction, related work, experiments, or limitations section; reverse-engineering how accepted AAAI/ACL/NeurIPS/ICLR/ICML papers are written; reducing generic AI-sounding prose; enforcing claim boundaries between exact, proxy, and related-only results; or running a repeated manuscript revision loop that keeps numbers and artifacts in sync.

Venue-agnostic protocol for evidence-grounded paper writing. Substitute your own venue,
manuscript path, and evidence ledger where this refers to them generically.

## Core Rule

Every number, claim, and comparison in the manuscript traces to a named artifact. If the
artifact cannot be produced, the sentence does not go in the paper.

## Claim Boundary Discipline

Classify every result before writing prose about it:

| Class | Meaning | Allowed phrasing |
|---|---|---|
| **exact** | Measured under this paper's protocol | Direct claim |
| **proxy** | Measured under a near but non-identical setup | "under proxy setting X" |
| **related-only** | Reported by other work under a different protocol | Cite, never compare as if equal |

Never present a proxy as official. Never compare an external paper's score against your
own as though the protocols matched — unless you actually ran your method on their
benchmark under a comparable protocol.

## The Four-Phase Revision Loop

Each pass does exactly this, then stops. Do not re-summarize the whole project.

1. **Check 1** — inspect current manuscript/PDF state and verify the target evidence
   artifact *before* editing.
2. **Edit 1** — one scoped change: a section, table, figure, or caption.
3. **Check 2** — compile, then run the strongest available sanity checks: page count,
   stale-number grep, undefined references, claim/artifact consistency.
4. **Edit 2** — fix at least one issue Check 2 found, or explicitly log why no safe
   second edit exists.
5. **Final check** — rerun the relevant lightweight verification.

Pick one target per pass: abstract, introduction motivation, contributions,
related-work positioning, benchmark design, one experiment subsection, limitations,
reproducibility checklist, supplement, or tables/captions.

## Cards To Draft Before Editing

**Claim card** — the claim, the artifact path backing it, and its boundary condition.

**Story card** — six slots:

- the tension in the field;
- the variable prior work left out;
- your protocol move;
- the verified result;
- the boundary or failure mode;
- the transition to the next section.

## Real-Meaning Pass

Before committing prose, check that:

- background is a concrete problem in the field, not generic "LLMs are powerful" framing;
- significance names the actual decision the section improves;
- experiment prose states artifact, split, seed, metric, and status clearly enough to
  reproduce;
- innovation ties to a specific control, evidence chain, or measured gap;
- result prose earns interest through contrast and boundary, not adjectives.

## Imitating Accepted Papers

Use official sources only — ACL Anthology, OpenReview, PMLR/ICML pages, NeurIPS
proceedings, the venue's own author kit and policy pages. Do not source claims about
venue, contribution, or review scores from blog summaries.

Build a pool of ~30 papers weighted toward your paper's type (benchmark/dataset, method,
analysis, position). For each, extract only writing-relevant features:

| Field | What to capture |
|---|---|
| Venue/type | benchmark, method, analysis, system, dataset |
| Abstract move | how it opens, states the gap, contribution, result, boundary |
| Introduction tension | the concrete problem pressure |
| Contribution structure | how many, and the verbs used |
| Related-work positioning | how it differentiates without overclaiming |
| Result narrative | which numbers get named in prose |
| Limitation style | integrated or buried |
| Reusable pattern | the sentence *shape* to imitate |

Imitate rhetorical structure, never wording. Patterns that travel well:

- "A high aggregate score would be sufficient if the question ended at X. It does not."
- "The pattern is diagnostic rather than uniformly positive."
- "This result supports X under Y controls; it does not imply Z."
- "We treat baselines as evidence probes, not standalone solutions."

## De-AI-Flavor Checks

Flag prose that has:

- generic adjectives with no concrete evidence attached;
- a contribution list that reads like a module inventory;
- no failure mode or limitation anywhere;
- no mention of split, metric, baseline status, or evidence boundary;
- repeated paragraph openings like "In recent years…".

## Submission Package Sync

Treat the work as a package, not a main-TeX file: main paper, supplement/appendix,
reproducibility checklist, bibliography and style files, generated tables, every
referenced figure, and the code/data artifact manifest.

When a main-paper claim, metric, figure, or release label changes, synchronize the
supplement, checklist, captions, and manifest in the same pass when feasible. If that is
too large for the current pass, log it as the next blocking sync target. Never leave a
required submission artifact contradicting the main paper.

## Venue Format Compliance

- Keep the official style files unmodified.
- Do not add banned packages, or margin/spacing/font-size/page-break hacks.
- Stay within the page limit; place figures near the sections discussing them; size them
  for the column layout without overflow.
- If content exceeds the limit, compress or move material to the supplement before
  adding anything new.
- Distinguish a local preview toolchain from formal source compliance. Final upload uses
  the official unmodified author kit and the venue's expected compile path.

## Hard Stops

Do not:

- invent missing results;
- write a number without an artifact path;
- force a story the evidence does not support;
- add unsupported causal explanations;
- promote partial or in-progress results as complete;
- label a proxy as official;
- compare external scores as if they were yours;
- add formatting hacks that risk submission compliance;
- ignore a compile error after editing;
- leave required artifacts with stale labels or numbers;
- silently overwrite user edits in a dirty worktree.

## Iteration Log

Append one entry per pass: timestamp, target section, files read, Check 1 / Edit 1 /
Check 2 / Edit 2 / final-check summary, claim/evidence/boundary, story check,
real-meaning check, files changed, compile status, format risks, package sync status,
evidence verification status with artifact path, next target.
