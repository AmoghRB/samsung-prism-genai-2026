"""Query-preprocessing + Matryoshka-dim sweep on a model whose doc embeddings are cached."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bench import load, metrics, embed
from run_dense import MODELS
from src.preprocess import preprocess_query
import numpy as np
key, modes = sys.argv[1], sys.argv[2].split(",")
cfg = MODELS[key]; D = load(); dids = list(D["corpus"]); qids = list(D["queries"])
E_d, _ = embed(cfg["name"], [D["corpus"][d] for d in dids], "doc", 512, cfg["dp"])
for mode in modes:
    E_q, _ = embed(cfg["name"], [preprocess_query(D["queries"][q], mode) for q in qids], f"query-{mode}", 512, cfg["qp"])
    for dim in [None, 512, 256, 128]:
        a, b = (E_q, E_d) if dim is None else (E_q[:, :dim], E_d[:, :dim])
        a = a / np.linalg.norm(a, axis=1, keepdims=True); b = b / np.linalg.norm(b, axis=1, keepdims=True)
        m, _ = metrics(a @ b.T, qids, dids, D["qrels"])
        rec = dict(model=key, qmode=mode, dim=dim or a.shape[1], **m); print(rec)
        open(os.path.join(os.path.dirname(__file__), "results.jsonl"), "a").write(json.dumps(rec) + "\n")
