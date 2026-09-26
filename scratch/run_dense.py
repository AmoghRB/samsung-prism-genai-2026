"""python scratch/run_dense.py MODEL_KEY  -> prints metrics, appends to scratch/results.jsonl"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from bench import load, metrics, embed
import numpy as np

JCE_Q = "Find the most relevant code snippet given the following query:\n"
JCE_D = "Candidate code snippet:\n"
MODELS = {
    "jce05": dict(name="jinaai/jina-code-embeddings-0.5b", qp=JCE_Q, dp=JCE_D, kw={}),
    "crank": dict(name="nomic-ai/CodeRankEmbed", qp="Represent this query for searching relevant code: ", dp=None, kw={}),
    "sfr400": dict(name="Salesforce/SFR-Embedding-Code-400M_R", qp="Instruct: Given Code or Text, retrieval relevant content\nQuery: ", dp=None, kw={}),
    "gtemb": dict(name="Alibaba-NLP/gte-modernbert-base", qp=None, dp=None, kw={}),
    "granite": dict(name="ibm-granite/granite-embedding-english-r2", qp=None, dp=None, kw={}),
    "jv2code": dict(name="jinaai/jina-embeddings-v2-base-code", qp=None, dp=None, kw={}),
    "qwen3": dict(name="Qwen/Qwen3-Embedding-0.6B", qp="Instruct: Given a programming problem, retrieve the Python code that solves it\nQuery:", dp=None, kw={}),
}

if __name__ == "__main__":
    key = sys.argv[1]
    maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 512
    cfg = MODELS[key]
    D = load(); dids = list(D["corpus"]); qids = list(D["queries"])
    E_d, td = embed(cfg["name"], [D["corpus"][d] for d in dids], "doc", maxlen, cfg["dp"], **cfg["kw"])
    E_q, tq = embed(cfg["name"], [D["queries"][q] for q in qids], "query", maxlen, cfg["qp"], **cfg["kw"])
    S = E_q @ E_d.T
    m, _ = metrics(S, qids, dids, D["qrels"])
    rec = dict(model=key, maxlen=maxlen, **m, doc_s=round(td, 1), q_s=round(tq, 1))
    print(rec)
    with open(os.path.join(os.path.dirname(__file__), "results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
