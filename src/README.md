# src/

Pipeline code. Empty until the baseline lands — see `../PROGRESS.md`.

Intended modules:

- `index.py` — chunk a corpus into snippets, build BM25 + dense indexes
- `query.py` — query analysis, hybrid retrieval, reranking
- `evaluate.py` — MTEB `AppsRetrieval` wrapper, emits `appsretrieval_results.json`
