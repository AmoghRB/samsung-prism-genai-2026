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
DEFAULT = PipelineConfig(model="Alibaba-NLP/gte-modernbert-base")
