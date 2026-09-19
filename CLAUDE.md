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
- **Efficiency is scored.** FAQ Q31: running time, GPU requirement and model size
  are factored into evaluation. Never report an accuracy gain without its latency
  and model-size cost. A slower, bigger pipeline needs to justify itself.
- **Target language is Python.** FAQ Q30: ignore the JavaScript codebase in the
  PPT and the JS example in the theme guide. The APPS dataset is Python.
- **Build to 25 Sep 2026.** The FAQ and deck both say 25 Sep; the 18 Sep
  registration email says 27 Sep. Unresolved — treat 26–27 as buffer that may not
  exist.
- **The tagged commit is what's judged** — release tag `PRISM_GENAI_HACKATHON_Y2026`.
  Not `main`, not the latest commit. The tag.
- **The repo must be public.**

## The score is not only NDCG
Screening ranks on NDCG@10/MRR, but the hands-on round is scored 30% working
prototype, 25% technical depth, 20% innovation, 15% theme relevance, 10%
presentation & documentation (FAQ Q22). A working, well-documented, defensible
prototype beats a marginally better number with a thin story. This is why the
README and PROGRESS log are treated as deliverables, not chores.

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
- **Log AI-assisted work in `PROGRESS.md` as it happens.** The mandatory AI
  disclosure form needs, per feature: which AI tool, the prompt, a summary of the
  output, and what was modified afterwards. Reconstructing that on the 25th is
  miserable — capture it daily.
- Keep [`SUBMISSION.md`](SUBMISSION.md) ticked off as things land. Three risks are
  still open: the team name on record, the 25-vs-27 Sep deadline, and whether
  Theme 1 test suites were released on 16 Sep.

## Reference material
Everything is in `docs/` — see `docs/README.md` for the index.
`theme1_guidelines.pdf` is the spec, but the **FAQ overrides it** where they
conflict (notably the JS-vs-Python question). When in doubt, re-read both rather
than working from memory.

The participant kit shipped with the registration email is for **Theme 5
(Interruptible Agents)**, not ours, despite its "all-themes" filename. There is
no starter harness for Theme 1 — we build the evaluation wrapper ourselves.
