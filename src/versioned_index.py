"""Version-aware snippet index (P1) with cross-version search (Bonus).

Design: embeddings are **content-addressed**. Each snippet's vector is stored
under the SHA-1 of its code, and each version is just a manifest listing which
(snippet id, hash) pairs it contains. Indexing a new version therefore only
embeds snippets whose code actually changed; everything else is a cache hit.
A typical commit touches a handful of functions, so re-indexing is near-instant
instead of a full rebuild.

Cross-version ("evolutionary") search has a specific failure mode the theme
guide calls out: versions of the same function are near-identical, so a plain
top-k fills up with five copies of one function. We rank *lineages* instead --
a lineage is every version of one snippet id -- and report, per lineage, the
best-matching version plus which other versions share or differ from it.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

import numpy as np

from .chunking import Snippet, chunk_directory


@dataclass
class Hit:
    score: float
    id: str
    path: str
    name: str
    start: int
    end: int
    code: str
    version: str
    also_in: list[str]  # other versions containing this exact code


class VersionedIndex:
    def __init__(self, store: str, retriever):
        self.store = store
        self.retriever = retriever
        os.makedirs(store, exist_ok=True)
        self._vec_path = os.path.join(store, "vectors.npy")
        self._meta_path = os.path.join(store, "index.json")
        if os.path.exists(self._meta_path):
            meta = json.load(open(self._meta_path))
            self.hashes: list[str] = meta["hashes"]
            self.versions: dict[str, list[dict]] = meta["versions"]
            self.order: list[str] = meta["order"]
            self.vectors = np.load(self._vec_path)
        else:
            self.hashes, self.versions, self.order = [], {}, []
            self.vectors = np.zeros((0, 0), dtype=np.float32)
        self._row = {h: i for i, h in enumerate(self.hashes)}

    # ---------- build ----------
    def add_version(self, name: str, root: str | None = None, snippets: list[Snippet] | None = None) -> dict:
        t0 = time.time()
        if snippets is None:
            snippets = chunk_directory(root)
        recs = [s.to_dict() for s in snippets]
        new = {}
        for r in recs:
            if r["hash"] not in self._row and r["hash"] not in new:
                new[r["hash"]] = r["code"]
        t_embed = time.time()
        if new:
            vec = self.retriever.encode_docs(list(new.values()))
            self.vectors = vec if self.vectors.size == 0 else np.vstack([self.vectors, vec])
            for h in new:
                self._row[h] = len(self.hashes); self.hashes.append(h)
        t_embed = time.time() - t_embed
        for r in recs:
            r.pop("code")  # code lives in the manifest only once per hash
        self.versions[name] = recs
        if name not in self.order:
            self.order.append(name)
        # keep code by hash so we can show results without the source tree
        codes_path = os.path.join(self.store, "code.json")
        codes = json.load(open(codes_path)) if os.path.exists(codes_path) else {}
        codes.update({h: c for h, c in new.items()})
        json.dump(codes, open(codes_path, "w"))
        self._save()
        return dict(version=name, snippets=len(recs), newly_embedded=len(new),
                    reused=len(recs) - sum(1 for r in recs if r["hash"] in new),
                    embed_s=round(t_embed, 2), total_s=round(time.time() - t0, 2))

    def _save(self):
        np.save(self._vec_path, self.vectors)
        json.dump(dict(hashes=self.hashes, versions=self.versions, order=self.order), open(self._meta_path, "w"))

    # ---------- search ----------
    def _code(self, h):
        if not hasattr(self, "_codes"):
            self._codes = json.load(open(os.path.join(self.store, "code.json")))
        return self._codes[h]

    def search(self, query: str, version: str | None = None, k: int = 10) -> list[Hit]:
        """version=None -> latest; version='all' -> evolutionary search."""
        if version == "all":
            return self._search_all(query, k)
        version = version or self.order[-1]
        recs = self.versions[version]
        rows = np.array([self._row[r["hash"]] for r in recs])
        scores = self.retriever.score(query, self.vectors[rows], [self._code(r["hash"]) for r in recs])
        top = np.argsort(-scores)[:k]
        where = self._hash_versions()
        return [self._hit(recs[i], float(scores[i]), version, where) for i in top]

    def _hash_versions(self):
        where: dict[str, list[str]] = {}
        for v in self.order:
            for r in self.versions[v]:
                where.setdefault(r["hash"], []).append(v)
        return where

    def _hit(self, r, s, version, where):
        return Hit(s, r["id"], r["path"], r["name"], r["start"], r["end"], self._code(r["hash"]),
                   version, [v for v in where.get(r["hash"], []) if v != version])

    def _search_all(self, query: str, k: int) -> list[Hit]:
        # Score every distinct piece of code once (identical code across
        # versions shares a vector), then collapse to one hit per lineage.
        where = self._hash_versions()
        latest_rec: dict[str, dict] = {}   # hash -> a record carrying it (latest version wins)
        latest_ver: dict[str, str] = {}
        for v in self.order:
            for r in self.versions[v]:
                latest_rec[r["hash"]] = r; latest_ver[r["hash"]] = v
        hs = list(latest_rec)
        rows = np.array([self._row[h] for h in hs])
        scores = self.retriever.score(query, self.vectors[rows], [self._code(h) for h in hs])
        rank = {v: i for i, v in enumerate(self.order)}
        best: dict[str, tuple] = {}
        for h, s in zip(hs, scores):
            r = latest_rec[h]
            # within a lineage: higher score wins; near-ties go to the newer version
            key = (round(float(s), 3), rank[latest_ver[h]])
            if r["id"] not in best or key > best[r["id"]][0]:
                best[r["id"]] = (key, h, float(s))
        ranked = sorted(best.values(), key=lambda x: -x[2])[:k]
        return [self._hit(latest_rec[h], s, latest_ver[h], where) for _, h, s in ranked]
