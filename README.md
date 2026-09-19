# Agentic Code Intelligence — Semantic Code Retrieval

**Samsung PRISM GenAI Hackathon 3.0 (Y2026) · Theme 1 · Team MSRIT_Waypoint**

Given a library of code and a natural-language query, return the code snippets
ranked by how relevant they are to that query.

> **Status: in development.** The retrieval pipeline is being built during
> 19–25 Sep 2026. Sections marked _WIP_ are not implemented yet. This notice
> comes down when the pipeline runs end-to-end.

---

## The problem

Finding the right block of code is the bottleneck in working with an unfamiliar
codebase, and it gets worse as the codebase grows. This is a **retrieval**
problem, not a generation one — given the query *"How is the input preprocessed
before going to the main function?"*, the job is to rank a `normalize()` helper
above an unrelated `check()` function.

Answer generation, explanation, and anything downstream of retrieval is
explicitly **out of scope** for this theme.

### Why not just ask an LLM to rank them?

The snippet library runs to thousands of snippets, and they get long. They do
not fit in any LLM's context window. Retrieval is also the *first* step of a RAG
pipeline and is expected to be faster than the generation that follows it —
an LLM ranking pass over long text is too slow to sit there.

---

## Goals, in priority order

| Priority | Goal | What it means |
|---|---|---|
| **P0** | Retrieval accuracy | Rank relevant snippets highest. Scored by NDCG@10 and MRR. |
| **P1** | Retrieval across versions | Codebases change constantly. Indexes and caches must rebuild for a new version in reasonable time. |
| **Bonus** | Evolutionary retrieval | Retrieve across *all* versions at once. Hard because versions of the same snippet are near-identical and must still be ranked sensibly. |

### Hard constraint: CPU only

The solution is expected to run on **CPU with minimal GPU utilisation**. Every
model choice here is constrained by that — no large rerankers, no models that
need a GPU to hit acceptable latency.

---

## Approach

The design assumption is that a single dense-embedding pass will not be
competitive on its own. The pipeline is staged so each stage can be measured and
kept or dropped on evidence.

```
query
  │
  ├─ 1. query analysis      classify intent, expand/rewrite
  │
  ├─ 2. hybrid retrieval    BM25 (lexical)  ┐
  │                          dense embeddings ┘ → fused candidate set
  │
  ├─ 3. rerank              cross-encoder over top-K only (CPU budget)
  │
  └─ ranked snippets
```

**1. Query analysis** — NL queries and code live in different vocabularies.
Classifying the query (is it asking about control flow? a specific API? an
error?) and rewriting it toward code-like terms is the cheapest available win.

**2. Hybrid retrieval** — lexical matching catches exact identifiers that
embeddings blur away; dense embeddings catch paraphrase that lexical matching
misses. Neither is sufficient alone. Scores are fused into one candidate set.

**3. Reranking** — a cross-encoder is far more accurate than bi-encoder cosine
similarity but far more expensive, so it only ever sees the top-K candidates.
K is a tunable knob against the CPU budget.

Snippet-side preprocessing (splitting on function boundaries, stripping or
keeping comments, attaching signatures as context) is treated as a first-class
variable, not an afterthought — the unit that gets indexed matters as much as
the model that indexes it.

---

## Evaluation

Screening is a competitive ranking on **P0 retrieval accuracy**, measured on the
test split of the [CoIR `apps`](https://huggingface.co/datasets/CoIR-Retrieval/apps)
dataset via the [MTEB](https://docs.mteb.org/) library.

- Task: `AppsRetrieval`
- Metrics: **NDCG@10** and **MRR**

The evaluation is run by wrapping the pipeline in an MTEB encoder:

```python
import json
import mteb
from mteb.models.abs_encoder import AbsEncoder

class PrePostPipelineEncoder(AbsEncoder):
    ...  # the pipeline described above

def main() -> None:
    model = PrePostPipelineEncoder()
    task = mteb.get_task("AppsRetrieval")
    result = mteb.evaluate(model, [task], encode_kwargs={"batch_size": 64})

    task_result = list(result.task_results)[0]
    with open("appsretrieval_results.json", "w") as f:
        json.dump(task_result.to_dict(), f, indent=2)
```

The resulting `appsretrieval_results.json` is attached to the tagged GitHub
release. See [`SUBMISSION.md`](SUBMISSION.md) for the full checklist.

---

## Running it

> _WIP — these commands are the intended interface and do not all work yet._

```bash
git clone https://github.com/AmoghRB/samsung-prism-genai-2026.git
cd samsung-prism-genai-2026
pip install -r requirements.txt
```

Index a codebase and query it:

```bash
python -m src.index  --corpus path/to/code --out .index/
python -m src.query  --index .index/ --q "how is input validated before parsing?"
```

Reproduce the screening numbers:

```bash
python -m src.evaluate        # writes appsretrieval_results.json
```

### Docker

```bash
docker build -t code-retrieval .
docker run --rm -it code-retrieval
```

---

## Repository layout

```
.
├── src/                 pipeline: indexing, retrieval, reranking, evaluation
├── docs/                theme guides, deck, and reference PDFs
├── SUBMISSION.md        deliverables checklist and deadlines
├── PROGRESS.md          dated build log
├── Dockerfile
└── requirements.txt
```

---

## Team

**MSRIT_Waypoint** — M. S. Ramaiah Institute of Technology, Bengaluru

- Amogh R B — [@AmoghRB](https://github.com/AmoghRB)
- Pankaj

---

## Acknowledgements

Built for the Samsung PRISM GenAI Hackathon 3rd Edition. Evaluation uses the
[MTEB](https://github.com/embeddings-benchmark/mteb) benchmark library and the
[CoIR](https://huggingface.co/CoIR-Retrieval) code-retrieval dataset collection.
