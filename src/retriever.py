"""The retrieval pipeline: pre-process -> CPU embedding -> similarity ranking.

Everything the benchmark, the CLI and the versioned index use goes through
`CodeRetriever`, so the number we report is produced by exactly the code the
jury will run.
"""
from __future__ import annotations

import os
import time

import numpy as np

from .config import PipelineConfig, DEFAULT
from .preprocess import preprocess_code, preprocess_query


class CodeRetriever:
    def __init__(self, cfg: PipelineConfig = DEFAULT, device: str = "cpu"):
        self.cfg = cfg
        self.device = device
        self._model = None

    # lazy so `--help` and index inspection don't pay model-load time
    @property
    def model(self):
        if self._model is None:
            import torch
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(self.cfg.threads or os.cpu_count())
            t0 = time.time()
            self._model = SentenceTransformer(self.cfg.model, device=self.device,
                                              trust_remote_code=True, revision=self.cfg.revision)
            self._model.max_seq_length = self.cfg.max_len
            self.load_s = time.time() - t0
        return self._model

    def _encode(self, texts: list[str], prompt: str | None, batch_size: int, progress: bool) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        # Longest-first batching: far less padding waste on CPU.
        order = np.argsort([-len(t) for t in texts])
        emb = self.model.encode([texts[i] for i in order], batch_size=batch_size, prompt=prompt,
                                normalize_embeddings=True, convert_to_numpy=True,
                                show_progress_bar=progress)
        emb = emb[:, : self.cfg.dim] if self.cfg.dim else emb     # Matryoshka truncation
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        out = np.empty_like(emb); out[order] = emb
        return out.astype(np.float32)

    @property
    def dim(self) -> int:
        return self.cfg.dim or self.model.get_sentence_embedding_dimension()

    def encode_queries(self, texts, batch_size=16, progress=False):
        return self._encode([preprocess_query(t, self.cfg.query_mode) for t in texts],
                            self.cfg.query_prompt, batch_size, progress)

    def encode_docs(self, texts, batch_size=16, progress=False):
        return self._encode([preprocess_code(t, self.cfg.doc_mode) for t in texts],
                            self.cfg.doc_prompt, batch_size, progress)

    def score(self, query: str, doc_vecs: np.ndarray, doc_texts=None) -> np.ndarray:
        q = self.encode_queries([query])[0]
        return doc_vecs @ q

    @staticmethod
    def top_k(qv: np.ndarray, dv: np.ndarray, k: int, chunk: int = 1024):
        """Exact cosine top-k, chunked so memory stays flat for big corpora."""
        idx = np.empty((len(qv), k), dtype=np.int64); val = np.empty((len(qv), k), dtype=np.float32)
        for s in range(0, len(qv), chunk):
            sc = qv[s:s + chunk] @ dv.T
            part = np.argpartition(-sc, kth=min(k, sc.shape[1] - 1), axis=1)[:, :k]
            ps = np.take_along_axis(sc, part, 1)
            o = np.argsort(-ps, axis=1)
            idx[s:s + chunk] = np.take_along_axis(part, o, 1)
            val[s:s + chunk] = np.take_along_axis(ps, o, 1)
        return idx, val
