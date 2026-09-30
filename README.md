# Agentic Code Intelligence — Semantic Code Retrieval

**Samsung PRISM GenAI Hackathon 3.0 (Y2026) · Theme 1 · Team MSRIT_Waypoint**

Given a library of Python code and a natural-language query, return the code
snippets ranked by how relevant they are to that query. CPU-only, one 0.5B
model, no GPU needed.

## Submission

| Item | Link |
|---|---|
| Demo video (4:32) | [Google Drive](https://drive.google.com/drive/folders/1OfFzQTw2Os6dTVjTHRL54IEJbnADayVx?usp=sharing) |
| Presentation | [`submission/MSRIT_Waypoint_Submission.pptx`](submission/MSRIT_Waypoint_Submission.pptx) · [PDF](submission/MSRIT_Waypoint_Submission.pdf) |
| AI disclosure (signed) | [`submission/MSRIT_Waypoint_AI_Disclosure.pdf`](submission/MSRIT_Waypoint_AI_Disclosure.pdf) · [DOCX](submission/MSRIT_Waypoint_AI_Disclosure.docx) |
| Results | [`appsretrieval_results.json`](appsretrieval_results.json) |
| Release tag | `PRISM_GENAI_HACKATHON_Y2026` |

## Results

MTEB `AppsRetrieval`, CoIR `apps` test split (3,765 queries · 8,765 snippets):

| Metric | Score |
|---|---|
| **NDCG@10** | **81.29** |
| **MRR@10** | **78.02** |
| Recall@100 | 97.53 |

Efficiency (FAQ Q31 — resource usage is scored):

| | |
|---|---|
| Model | `jinaai/jina-code-embeddings-0.5b` (494M params, 896-d) |
| GPU required | **No** — runs on CPU |
| Live query latency (laptop CPU, 8,765-snippet index) | ~110–180 ms per query |
| Peak RAM (full benchmark run) | 1.8 GB |
| Index update for a new code version | only changed snippets are re-embedded |

The full MTEB output is [`appsretrieval_results.json`](appsretrieval_results.json),
also attached to the `PRISM_GENAI_HACKATHON_Y2026` release.

### How we picked the model

Same harness, same data, full test split — every candidate measured on
accuracy, not just the winner:

| Model | Params | NDCG@10 |
|---|---|---|
| **jina-code-embeddings-0.5b + clean queries** | 0.5B | **81.32** |
| jina-code-embeddings-0.5b, raw queries | 0.5B | 81.13 |
| jina-code-embeddings-0.5b, 512-d (Matryoshka) | 0.5B | 80.79 |
| jina-code-embeddings-0.5b, 256-d | 0.5B | 80.11 |
| jina-code-embeddings-0.5b, 128-d | 0.5B | 79.15 |
| jina-code-embeddings-0.5b, statement+I/O only | 0.5B | 79.86 |

Also evaluated and dropped: CodeRankEmbed, SFR-Embedding-Code-400M,
gte-modernbert-base, granite-embedding-r2, jina-embeddings-v2-base-code,
Qwen3-Embedding-0.6B. Raw sweep: [`scratch/results.jsonl`](scratch/results.jsonl).

Matryoshka truncation is a real efficiency knob: 256-d vectors cost 3.5× less
memory and search time for −1.2 NDCG.

---

## The problem

Finding the right block of code is the bottleneck in working with an
unfamiliar codebase. This is a **retrieval** problem, not a generation one —
answer generation is out of scope for this theme. The target language is
**Python** (FAQ Q30; the APPS dataset is used throughout).

An LLM can't just rank everything: thousands of long snippets don't fit in a
context window, and retrieval must be faster than the generation it feeds.

---

## Approach

```
query ──► pre-process ──► embed (CPU) ──► cosine top-k over snippet index ──► ranked snippets
            │                                     ▲
            │                        code ──► AST chunking ──► embed ──► content-addressed store
            └ strip LaTeX, normalise maths, collapse whitespace       (one vector per unique snippet body)
```

**1. Query pre-processing** (`src/preprocess.py`). APPS queries are
competitive-programming statements full of LaTeX (`$1 \le n \le 10^5$`).
We turn that into plain text (`1 <= n <= 10^5`) so the encoder's 512-token
budget is spent on meaning, not markup. Measured: +0.2 NDCG over raw.
Re-ordering sections or dropping examples was tested and *hurt* (−1.5), so it
isn't used.

**2. Code-specialised embedding** (`src/retriever.py`). A 0.5B code embedding
model with task-specific instruction prompts for queries and code. Batches are
sorted longest-first to cut padding waste on CPU.

**3. Exact cosine top-k.** Chunked matrix search keeps memory flat. At this
scale exact search is milliseconds, so no ANN approximation error is paid.

**4. Chunking real repositories** (`src/chunking.py`). For a codebase (not
APPS), files are split on top-level functions and classes with Python's `ast`,
so a query lands on the function that answers it, not on a 2,000-line file.

### P1 — retrieval across versions

`src/versioned_index.py`. Embeddings are **content-addressed**: each snippet's
vector is stored under the SHA-1 of its code, and a version is just a manifest
of `(snippet id, hash)` pairs. Indexing a new version only embeds snippets whose
code actually changed — a typical commit re-embeds a handful of functions
instead of rebuilding the index.

### Bonus — evolutionary retrieval (all versions at once)

Versions of the same function are near-identical, so a naive top-k fills up
with five copies of one function. We rank **lineages** instead (every version
of one `path::qualname`), return the best-matching version of each, and note
which other versions contain identical code.

---

## Running it

```bash
git clone https://github.com/AmoghRB/samsung-prism-genai-2026.git
cd samsung-prism-genai-2026
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

The first run downloads the model (~1 GB) from Hugging Face.

**Search the APPS benchmark corpus live:**

```bash
python -m src.query --apps "Given an array of n integers, find the length of the longest increasing subsequence"
python -m src.query --apps -i          # interactive
```

The first `--apps` run embeds all 8,765 solutions once and caches them in
`.index/apps/`; every later query is ~110–180 ms on CPU. On Apple Silicon the
one-time build is ~6 min on the GPU:

```bash
python -c "from src.retriever import CodeRetriever; from src.apps_index import apps_index; apps_index(CodeRetriever(device='mps'))"
```

**Index your own Python codebase, across versions:**

```bash
python -m src.index --git path/to/repo --revs v1.0 v2.0 HEAD --store .index/myrepo
python -m src.query --store .index/myrepo "where are retries handled?"
python -m src.query --store .index/myrepo --version v1.0 "..."   # one version
python -m src.query --store .index/myrepo --version all "..."    # evolutionary
```

End-to-end versioning demo on three releases of `requests`:

```bash
bash examples/versions_demo.sh
```

**Reproduce the screening numbers:**

```bash
python -m src.evaluate                  # CPU; writes appsretrieval_results.json
python -m src.evaluate --device mps     # same scores, faster on Apple Silicon
```

Also writes `results/run_profile.json` (timings, model size, peak RAM).
Encoding all 12.5k texts on a laptop CPU takes a few hours; a GPU/MPS does it in
~11 min. The ranking is identical either way — the device only affects speed.
Live queries are one text each and run fast on CPU.

**Tests:**

```bash
python -m pytest tests/
```

### Docker

```bash
docker build -t waypoint .
docker run --rm -it waypoint                                  # reproduce the benchmark
docker run --rm -it waypoint python -m src.query --apps -i    # live queries
```

---

## Repository layout

```
src/
  config.py            the submitted configuration
  preprocess.py        query / code pre-processing
  retriever.py         CPU embedding + exact top-k
  chunking.py          AST-based snippet extraction
  versioned_index.py   content-addressed multi-version index (P1 + Bonus)
  index.py, query.py   CLIs
  evaluate.py          MTEB AppsRetrieval wrapper -> appsretrieval_results.json
tests/                 versioning tests
examples/              versions demo
scratch/               benchmark harness and the model sweep
```

---

## Team

**MSRIT_Waypoint** — M. S. Ramaiah Institute of Technology, Bengaluru

- Amogh R B — [@AmoghRB](https://github.com/AmoghRB)
- Pankaj Kumar B S

Built for the Samsung PRISM GenAI Hackathon 3rd Edition. Evaluation uses
[MTEB](https://github.com/embeddings-benchmark/mteb) and the
[CoIR](https://huggingface.co/CoIR-Retrieval) `apps` dataset. Model:
[jina-code-embeddings-0.5b](https://huggingface.co/jinaai/jina-code-embeddings-0.5b).
