"""Fast experiment harness: embed corpus+queries once, cache, score NDCG@10/MRR@10.

usage: python scratch/bench.py MODEL [--qprep NAME] [--dprep NAME] [--maxlen N]
"""
import argparse, hashlib, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE, exist_ok=True)


def load():
    p = os.path.join(CACHE, "apps.json")
    if os.path.exists(p):
        return json.load(open(p))
    import mteb
    t = mteb.get_task("AppsRetrieval"); t.load_data()
    d = t.dataset["default"]["test"]
    out = {
        "corpus": {x["id"]: x["text"] for x in d["corpus"]},
        "queries": {x["id"]: x["text"] for x in d["queries"]},
        "qrels": {k: list(v.keys())[0] for k, v in d["relevant_docs"].items()},
    }
    json.dump(out, open(p, "w"))
    return out


def metrics(scores, qids, dids, qrels):
    """scores: [nq, nd] matrix. Returns ndcg@10, mrr@10, recall@100, full ranks."""
    did_idx = {d: i for i, d in enumerate(dids)}
    gold = np.array([did_idx[qrels[q]] for q in qids])
    gscore = scores[np.arange(len(qids)), gold]
    rank = (scores > gscore[:, None]).sum(1) + 1  # 1-based
    ndcg = np.where(rank <= 10, 1 / np.log2(rank + 1), 0).mean()
    mrr = np.where(rank <= 10, 1 / rank, 0).mean()
    r100 = (rank <= 100).mean()
    return dict(ndcg10=round(ndcg * 100, 2), mrr10=round(mrr * 100, 2),
                r1=round((rank == 1).mean() * 100, 2), r100=round(r100 * 100, 2)), rank


def embed(model_name, texts, tag, maxlen=512, prompt=None, bs=16, device="mps", **kw):
    key = hashlib.md5(f"{model_name}|{tag}|{maxlen}|{prompt}".encode()).hexdigest()[:12]
    p = os.path.join(CACHE, f"{model_name.replace('/', '_')}_{tag}_{key}.npy")
    if os.path.exists(p):
        return np.load(p), 0.0
    from sentence_transformers import SentenceTransformer
    import torch
    torch.set_num_threads(os.cpu_count())
    m = SentenceTransformer(model_name, device=device, trust_remote_code=True, **kw)
    m.max_seq_length = maxlen
    # sort by length for efficient batching
    order = np.argsort([-len(t) for t in texts])
    t0 = time.time()
    e = m.encode([texts[i] for i in order], batch_size=bs, normalize_embeddings=True,
                 show_progress_bar=True, prompt=prompt, convert_to_numpy=True)
    dt = time.time() - t0
    out = np.empty_like(e); out[order] = e
    np.save(p, out)
    print(f"[{tag}] {len(texts)} texts in {dt:.1f}s ({len(texts)/dt:.1f}/s)")
    return out, dt
