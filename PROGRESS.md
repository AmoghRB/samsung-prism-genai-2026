# Progress Log

Dated record of what actually got done. Appended to by `ship.sh` on every push.

## Benchmark runs

The number that matters is NDCG@10 on the CoIR `apps` test split. Every pipeline
change gets a row here, or it didn't happen.

| Date | Config | NDCG@10 | MRR | Notes |
|---|---|---|---|---|
| 2026-09-26 | jina-code-0.5b, raw queries, 896-d (bench harness) | 81.16 | 77.91 | first number on the board |
| 2026-09-26 | jina-code-0.5b, clean queries, 896-d | 81.32 | 78.07 | best in sweep; 512/256/128-d = 80.79/80.11/79.15 |
| 2026-09-26 | jina-code-0.5b, noex / iofirst queries | 79.86 / 77.33 | 76.53 / 73.65 | re-ordering sections hurts — dropped |
| **2026-09-29** | **Submitted: `python -m src.evaluate` (official MTEB path)** | **81.29** | **78.02** | R@100 97.53 · 494M params · 1.8 GB peak RAM · live query ~110–180 ms on CPU |

## Log

- **2026-09-19** — Repo scaffolded. README, submission checklist, and Claude
  instructions written from the Theme 1 guide. No pipeline code yet.
- **2026-09-19** — Official docs from the registration email added to `docs/`
  (FAQ v4, AI disclosure form, PPT template, participant kit). Read the FAQ.
  Four findings that change the plan:
  1. **Q30 — target Python, not JavaScript.** The PPT's JS codebase and the theme
     guide's JS example are both wrong; APPS (Python) is used throughout.
  2. **Q31 — efficiency is scored.** Running time, GPU requirement and model size
     are factored into evaluation. Accuracy gains must be weighed against cost.
  3. **Q22 — the rubric is broader than NDCG.** 30% working prototype, 25%
     technical depth, 20% innovation, 15% theme relevance, 10% presentation/docs.
  4. **Deadline conflict.** FAQ and deck say 25 Sep; the 18 Sep registration email
     says 27 Sep. Building to the 25th.
  Also: the "all-themes" participant kit is Theme 5 only — no starter code exists
  for Theme 1.

- **2026-09-29** — Submission day. Locked `DEFAULT` config to jina-code-embeddings-0.5b
  + clean queries (it still pointed at gte-modernbert). First run of the official
  `src.evaluate` path crashed writing the JSON (datetime field) — fixed with
  `default=str`, re-ran: NDCG@10 81.29 / MRR@10 78.02, matching the sweep.
  Bulk encoding on laptop CPU was ~40 s/batch (4–5 h total), so added `--device`
  and ran the benchmark on Apple MPS (~11 min); scores are device-independent.
  Live queries measured on CPU: ~110–180 ms. README rewritten with real numbers;
  SUBMISSION checklist updated; PPT and AI disclosure filled (kept local).

### AI usage log
The mandatory disclosure form needs per-feature detail: tool, prompt, output
summary, what was modified. Log it here as work happens.

- **2026-09-19** — Claude Code (Opus 5): scaffolded repo structure and wrote the
  README, SUBMISSION.md, CLAUDE.md and this log; extracted and summarised the
  official PDFs/DOCXs. Documentation only — no pipeline code written yet.

- **2026-09-19** — note repo is private and flag Samsung docs before going public

- **2026-09-29** — Claude Code (Opus 5.5): fixed the config and the MTEB JSON bug,
  added `--device`, ran the official evaluation, rewrote README/SUBMISSION, filled
  the submission PPT template and the AI disclosure form, wrote the demo script.
  Amogh reviews and signs the disclosure form and records the video.

- **2026-09-30** — fix versions demo: blobless clone made `git archive v2.31.0` fail mid-run; now full clone, git error surfaced, and the demo reuses a prebuilt index (`--rebuild` to re-embed). Verified: v2.31.0 +21 / v2.32.3 +78 new embeddings, ~120 ms/query on CPU.
