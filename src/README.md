# src/

See the top-level README for the pipeline description.

- `config.py` — the submitted configuration (`DEFAULT`)
- `preprocess.py` — query / code pre-processing
- `retriever.py` — CPU embedding + exact cosine top-k
- `chunking.py` — AST-based snippet extraction for real repos
- `versioned_index.py` — content-addressed multi-version index
- `index.py`, `query.py` — CLIs
- `apps_index.py` — the APPS corpus as a searchable index
- `evaluate.py` — MTEB `AppsRetrieval` wrapper, emits `appsretrieval_results.json`
