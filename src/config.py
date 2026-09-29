"""Pipeline configuration. The DEFAULT is the configuration we submit."""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PipelineConfig:
    model: str
    revision: str | None = None
    query_prompt: str | None = None
    doc_prompt: str | None = None
    query_mode: str = "clean"      # see preprocess.preprocess_query
    doc_mode: str = "raw"          # see preprocess.preprocess_code
    max_len: int = 512
    dim: int | None = None         # Matryoshka truncation; None = full
    threads: int | None = None     # torch CPU threads; None = all cores

    def to_dict(self):
        return asdict(self)


# Filled in from the benchmark sweep -- see PROGRESS.md.
# jina-code-embeddings-0.5b, clean queries, full 896-d: NDCG@10 81.32 / MRR@10 78.07
# on AppsRetrieval test (scratch/results.jsonl). Beat CodeRankEmbed, SFR-400M,
# gte-modernbert, granite-r2, jina-v2-code and Qwen3-0.6B in the same sweep.
DEFAULT = PipelineConfig(
    model="jinaai/jina-code-embeddings-0.5b",
    query_prompt="Find the most relevant code snippet given the following query:\n",
    doc_prompt="Candidate code snippet:\n",
    query_mode="clean",
)
