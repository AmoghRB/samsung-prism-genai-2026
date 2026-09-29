"""Official screening run: MTEB `AppsRetrieval`, test split -> appsretrieval_results.json

    python -m src.evaluate                 # submitted config, CPU only
    python -m src.evaluate --out my.json
    python -m src.evaluate --device mps    # same scores, faster bulk encoding on Apple GPU

The pipeline is plugged into MTEB as a `SearchProtocol` model (index + search),
so MTEB scores exactly our ranking -- including query pre-processing -- with
its own NDCG@10 / MRR implementation. Also writes `results/run_profile.json`
with wall-clock and resource numbers, because efficiency is scored (FAQ Q31).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import time

import numpy as np

from .config import DEFAULT
from .retriever import CodeRetriever


class PipelineSearch:
    """MTEB SearchProtocol adapter around CodeRetriever."""

    def __init__(self, retriever: CodeRetriever):
        from mteb.models.model_meta import ModelMeta
        self.r = retriever
        self.timings: dict[str, float] = {}
        self.mteb_model_meta = ModelMeta.create_empty(overwrites={
            "name": "MSRIT_Waypoint/code-retrieval-pipeline",
            "revision": "PRISM_GENAI_HACKATHON_Y2026",
            "model_type": ["dense"],
        })

    def index(self, corpus, *, task_metadata, hf_split, hf_subset, encode_kwargs, num_proc=None):
        t0 = time.time()
        self.doc_ids = list(corpus["id"])
        self.doc_vecs = self.r.encode_docs(list(corpus["text"]), progress=True)
        self.timings["index_s"] = time.time() - t0
        self.timings["n_docs"] = len(self.doc_ids)

    def search(self, queries, *, task_metadata, hf_split, hf_subset, top_k, encode_kwargs,
               top_ranked=None, num_proc=None):
        t0 = time.time()
        qids = list(queries["id"])
        qv = self.r.encode_queries(list(queries["text"]), progress=True)
        t_enc = time.time() - t0
        idx, val = self.r.top_k(qv, self.doc_vecs, top_k)
        self.timings.update(query_encode_s=t_enc, search_s=time.time() - t0 - t_enc,
                            n_queries=len(qids))
        return {q: {self.doc_ids[j]: float(s) for j, s in zip(idx[i], val[i])} for i, q in enumerate(qids)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="appsretrieval_results.json")
    ap.add_argument("--profile", default="results/run_profile.json")
    ap.add_argument("--device", default="cpu",
                    help="encoding device for the bulk benchmark run; scores do not depend on it")
    args = ap.parse_args()

    import mteb
    import torch
    t_start = time.time()
    retriever = CodeRetriever(DEFAULT, device=args.device)
    model = PipelineSearch(retriever)
    task = mteb.get_task("AppsRetrieval")
    result = mteb.evaluate(model, [task], encode_kwargs={"batch_size": 16}, overwrite_strategy="always")
    task_result = list(result.task_results)[0]
    with open(args.out, "w") as f:
        json.dump(task_result.to_dict(), f, indent=2, default=str)

    scores = task_result.scores["test"][0]
    n_params = sum(p.numel() for p in retriever.model.parameters())
    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024 if platform.system() == "Darwin" else 1024)
    prof = dict(
        config=DEFAULT.to_dict(),
        ndcg_at_10=scores["ndcg_at_10"], mrr_at_10=scores["mrr_at_10"],
        recall_at_100=scores.get("recall_at_100"),
        model_params_m=round(n_params / 1e6, 1),
        embed_dim=retriever.dim,
        device=args.device, torch_threads=torch.get_num_threads(),
        cpu=platform.processor() or platform.machine(), platform=platform.platform(),
        peak_rss_mb=round(rss_mb),
        total_wall_s=round(time.time() - t_start, 1),
        **{k: round(v, 2) if isinstance(v, float) else v for k, v in model.timings.items()},
    )
    prof["ms_per_query"] = round(1000 * (prof["query_encode_s"] + prof["search_s"]) / prof["n_queries"], 1)
    prof["docs_per_s"] = round(prof["n_docs"] / prof["index_s"], 1)
    os.makedirs(os.path.dirname(args.profile) or ".", exist_ok=True)
    json.dump(prof, open(args.profile, "w"), indent=2)
    print(json.dumps(prof, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
