# Submission Checklist — Samsung PRISM GenAI Hackathon 3.0

**Target: be finished by 25 Sep 2026. Hard deadline 27 Sep.** See the date
conflict below — build to the earlier date.

**Submission form:** https://forms.gle/ZWPsj6LoQqbQXmMz6 — one submission per
team, one theme (FAQ Q6).

**Queries:** `prism@samsung.com` (FAQ Q29) or reply to `binny.l@samsung.com`.

---

## ⚠️ Deadline conflict — unresolved

| Source | Date | Dated |
|---|---|---|
| Main deck | 25 Sep 2026 | — |
| **FAQ v4** (Q18, Q27) | **25 Sep 2026** | — |
| **Registration email** (Binny Lakra) | **27 Sep 2026** | 18 Sep 2026 |

The email is the **later** communication, and the FAQ's own closing note says
*"Participants should follow the latest official communication if any timeline
... is updated."* That argues for 27 Sep.

But two of three official documents say 25 Sep, and the email says *"Timings are
Sacrosanct."*

**Decision: build to 25 Sep.** Treat the 26th and 27th as buffer that may not
exist. Confirm the real date with the organisers — this is worth one email.

---

## Deliverables

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | GitHub repo, public or shared | ⚠️ **private** | Repo exists: `AmoghRB/samsung-prism-genai-2026`. Currently **private** — see below before flipping it public. |
| 2 | README, reproducible setup | ☑ draft | "Reproducible setup instructions" is the wording — test on a clean machine. |
| 3 | Dockerfile | ☐ | Explicitly named in FAQ Q17. |
| 4 | Release tag `PRISM_GENAI_HACKATHON_Y2026` | ☐ | **The tagged commit is judged.** All referenced material must be in that commit (FAQ Q19). |
| 5 | `appsretrieval_results.json` | ☐ | MTEB output, attached to the release. |
| 6 | Demo video, ≤ 5 min | ☐ | Live queries and responses — not just numbers. |
| 7 | PPT or PDF, their template | ☐ | Named `MSRIT_Waypoint_...` (FAQ Q12, Q21). |
| 8 | AI disclosure form | ☐ | Mandatory. Needs per-feature detail — see below. |
| 9 | Google Form submitted | ☐ | Don't finish at 11:58. |

### The release tag (FAQ Q20 — exact commands)

```bash
git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "PRISM Gen AI Hackathon Y2026 Final Submission"
git push origin PRISM_GENAI_HACKATHON_Y2026
```

---

## Rules clarified by the FAQ

### Theme 1 specifics

**Q30 — ignore the JavaScript codebase.** The PPT mentions a JS codebase; the
theme guide's worked example is also JS. Both are misleading. *"We would be
using the APPS dataset (Python) as mentioned in the theme guideline document
throughout the hackathon. Please ignore the Javascript codebase mentioned in the
PPT."* **Build and tune for Python.**

**Q31 — efficiency is scored, not just accuracy.** No restrictions on methods,
*"however ... the resource usage (running time, GPU requirement, model size,
etc.) would be factored in during the evaluation of a submission."*

> This changes the strategy. A heavy cross-encoder that wins on NDCG@10 but is
> slow and large can still lose. Every ranking gain has to be weighed against
> its latency and model-size cost, and both need to be **measured and reported**,
> not just the accuracy number.

### Evaluation rubric (Q22) — retrieval accuracy is not the whole score

| Weight | Dimension |
|---|---|
| 30% | Working prototype & functionality |
| 25% | Technical depth & feasibility |
| 20% | Innovation & originality |
| 15% | Relevance to theme |
| 10% | Presentation & documentation |

Screening ranks on NDCG@10/MRR, but the hands-on round uses the above. **A
working, well-documented, defensible prototype beats a marginally higher score
with a thin story.** The README and PPT are 10% on their own.

### Naming convention (Q12, Q21)
`CollegeName_TeamName` → **`MSRIT_Waypoint`**. Use it for the team and for the
presentation/submission filenames.

### Test suites (Q14)
Detailed test cases and test suites were *planned for release 16 Sep 2026*.
**We have not seen these.** Check whether they exist — if there's an official
test suite for Theme 1, it changes what we optimise against. Worth asking.

---

## AI disclosure form — start tracking now

`docs/LangAI3.0_AI_Disclosure.docx` requires, per feature:

1. Feature name
2. Self-Generated / AI-Generated / Both
3. **AI tool used, the prompt used, output summary, and what was modified**

> This is not something to reconstruct on the 25th. Log AI-assisted work in
> `PROGRESS.md` as it happens — which tool, roughly what was asked, what you
> changed afterwards. Ten minutes a day beats a panicked evening.

Also needs: team name, project name, institution, submission date, ethical
compliance confirmation, and a signed sign-off from the team representative.

---

## Open risks

### 1. Team name on record ⚠️ UNRESOLVED
Registration may have gone in as **MSRIT_Lodestar** before the rename to
**MSRIT_Waypoint**. The convention is `CollegeName_TeamName` and filenames must
match Samsung's record. **Action:** ask `prism@samsung.com` or reply to
`binny.l@samsung.com`.

### 2. Registration on record ✅ RESOLVED
The 18 Sep email confirms: *"You're officially registered for the Gen AI
Hackathon 3.0."*

### 3. Deadline 25 vs 27 Sep ⚠️ UNRESOLVED
See above. Mitigated by building to the 25th.

### 4. Samsung's own documents are in this repo ⚠️
`docs/` contains Samsung's theme guides, FAQ, PPT template and participant kit.
The repo must be public or shared by submission, but making it public as-is
republishes Samsung's material.

**Action before going public:** either move `docs/` out of the repo and gitignore
it, or share the repo privately with the judges instead (FAQ Q17 allows "public
**or shared**"). Do not flip this repo to public without handling that first.

### 5. CSV vs JSON
The theme guide's Screening section says "csv file", but the sample code and the
release instructions both produce and upload **JSON**. The FAQ doesn't address
it. **Produce the JSON** as the sample code specifies, and note it in the
release description.

---

## What the demo video must show

- **Not** just inference results or metric numbers — that fails the brief
- Actual responses to actual queries
- How **fast** the solution is — doubly important now that Q31 makes resource
  usage a scored dimension
- Ideally a hard query where the ranking is visibly good

---

## What the PPT must cover

- The approach in detail: which pre/post-processing steps, which embedding model
- Retrieval results for a tough query
- Resource profile — runtime, model size, CPU-only — given Q31
- Follow their template rather than redesigning it

---

## Timeline

Building to 25 Sep, with 26–27 as buffer that may not exist.

| Date | Milestone |
|---|---|
| 19 Sep | Repo scaffolded. Email organisers: team name, real deadline, Theme 1 test suites. |
| 20–21 Sep | **Build weekend.** Baseline MTEB run end-to-end → real NDCG@10 on the board. Then hybrid BM25 + dense. |
| 22–23 Sep | Query analysis and reranking. Every change measured on accuracy **and** latency/model size. |
| 24 Sep | Docker. Verify README on a clean machine. P1 versioning. |
| 25 Sep | Demo video, PPT, AI disclosure. **Tag and submit.** |
| 26–27 Sep | Buffer only. Do not plan work here. |
| 9 Oct | Top 15 announced |
| 15 Oct | Final demo round — present live, walk the jury through the prototype, defend design trade-offs (FAQ Q26) |
| 24 Oct | Final results |

---

## Prizes and outcomes (FAQ Q28)

Samsung R&D summer internships for selected students; winning teams may work on
a PRISM worklet with a Samsung mentor; certificates for shortlisted teams; merit
certificates for winners; publication opportunities; prizes worth **INR 1.5 lakh**.

---

## Evaluation stages

**Screening** — competitive ranking on P0 retrieval accuracy (NDCG@10, MRR) over
the CoIR `apps` test split. Top submissions advance.

**Hands-on** — jury reviews the PPT and demo video, runs the code on their own
queries, and evaluates **P1 (retrieval across versions)** and the **Bonus
(evolutionary retrieval)** goals, against the 30/25/20/15/10 rubric above.

> P1 and the Bonus are only assessed if you pass screening — but they're the
> hardest to retrofit. Design the index for versioning from the start.
