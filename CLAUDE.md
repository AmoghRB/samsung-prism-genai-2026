# Samsung Hackathon — Claude Code Instructions

@../CLAUDE.md

## What this is
Samsung PRISM GenAI Hackathon 3.0, **Theme 1: Agentic Code Intelligence**.
Team **MSRIT_Waypoint** (Amogh + Pankaj), MSRIT Bengaluru.

Natural-language query → ranked code snippets. **Retrieval only.** Answer
generation, explanation, or anything downstream of the ranking is out of scope
per the theme guide — don't build it, don't propose it.

## Hard constraints — do not violate
- **CPU only.** Minimal GPU utilisation is an explicit requirement. Reject any
  approach that needs a GPU to be fast enough.
- **Deadline 27 Sep 2026, 11:59 PM IST.** Confirmed by organiser email 18 Sep — supersedes the 25 Sep date in the deck. No slipping.
- **The tagged commit is what's judged** — release tag `PRISM_GENAI_HACKATHON_Y2026`.
  Not `main`, not the latest commit. The tag.
- **The repo must be public.**

## Priorities, in the theme's own order
1. **P0 — retrieval accuracy.** NDCG@10 and MRR on the CoIR `apps` test split,
   run through MTEB's `AppsRetrieval` task. This is the screening gate.
2. **P1 — retrieval across versions.** Indexes/caches must rebuild for a new
   code version in reasonable time.
3. **Bonus — evolutionary retrieval** across all versions at once.

Optimise P0 first — nothing else is scored until screening is passed. But design
the index so versioning isn't a rewrite later.

## Working guidelines
- **Measure every change.** This is a benchmark competition. Any pipeline change
  that isn't accompanied by an NDCG@10 / MRR delta is speculation. Keep a table
  of run → config → score in `PROGRESS.md`.
- **Baseline first.** A working end-to-end MTEB run with a plain off-the-shelf
  embedding model beats a clever pipeline that doesn't run. Get the number on
  the board, then improve it.
- **Don't over-engineer the demo.** The jury wants to see live queries answered
  fast, not a UI.
- **Verify the README on a clean machine** before the 25th. "Can be run by
  following the steps in the GitHub repo" is an explicit submission requirement.
- Keep [`SUBMISSION.md`](SUBMISSION.md) ticked off as things land. Flag the two
  open organiser risks (team name, registration date) until they're resolved.

## Reference material
The theme guides and main deck are in `docs/`. `theme1_guidelines.pdf` is the
authoritative spec — when in doubt, re-read it rather than working from memory.
The Theme 2 and Theme 4 PDFs have no text layer and need page rendering to read
(not relevant to us — we're Theme 1).
