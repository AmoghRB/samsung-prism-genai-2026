# Progress Log

Dated record of what actually got done. Appended to by `ship.sh` on every push.

## Benchmark runs

The number that matters is NDCG@10 on the CoIR `apps` test split. Every pipeline
change gets a row here, or it didn't happen.

| Date | Config | NDCG@10 | MRR | Notes |
|---|---|---|---|---|
| — | _no baseline yet_ | — | — | |

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

### AI usage log
The mandatory disclosure form needs per-feature detail: tool, prompt, output
summary, what was modified. Log it here as work happens.

- **2026-09-19** — Claude Code (Opus 5): scaffolded repo structure and wrote the
  README, SUBMISSION.md, CLAUDE.md and this log; extracted and summarised the
  official PDFs/DOCXs. Documentation only — no pipeline code written yet.

- **2026-09-19** — note repo is private and flag Samsung docs before going public
