"""Versioned index behaviour, with a deterministic fake encoder (no model download)."""
import hashlib
import numpy as np
from src.chunking import chunk_source
from src.versioned_index import VersionedIndex


class FakeRetriever:
    calls = 0
    def _v(self, t):
        # bag of words, hashed: identical text -> identical vector
        v = np.zeros(64, dtype=np.float32)
        for w in t.split():
            v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 64] += 1
        return v / (np.linalg.norm(v) or 1)
    def encode_docs(self, texts):
        FakeRetriever.calls += len(texts)
        return np.stack([self._v(t) for t in texts])
    def score(self, q, vecs, texts=None):
        return vecs @ self._v(q)


V1 = '''import sys

def parse_input(line):
    return [int(x) for x in line.split()]

def solve(nums):
    return max(nums)
'''
V2 = V1.replace("return max(nums)", "return max(nums) - min(nums)")


def test_chunking_functions_and_header():
    names = [s.name for s in chunk_source(V1, "a.py")]
    assert names == ["<module>", "parse_input", "solve"]


def test_incremental_reembeds_only_changes(tmp_path):
    idx = VersionedIndex(str(tmp_path), FakeRetriever())
    s1 = idx.add_version("v1", snippets=chunk_source(V1, "a.py"))
    s2 = idx.add_version("v2", snippets=chunk_source(V2, "a.py"))
    assert s1["newly_embedded"] == 3
    assert s2["newly_embedded"] == 1 and s2["reused"] == 2


def test_version_pinned_and_evolutionary_search(tmp_path):
    idx = VersionedIndex(str(tmp_path), FakeRetriever())
    idx.add_version("v1", snippets=chunk_source(V1, "a.py"))
    idx.add_version("v2", snippets=chunk_source(V2, "a.py"))
    assert idx.search("max min nums", version="v1", k=1)[0].version == "v1"
    assert idx.search("max min nums", k=1)[0].version == "v2"          # default = latest
    hits = idx.search("nums", version="all", k=10)
    ids = [h.id for h in hits]
    assert len(ids) == len(set(ids)) == 3                             # one hit per lineage
    parse = next(h for h in hits if h.name == "parse_input")
    assert parse.also_in                                              # unchanged -> shared


def test_index_persists(tmp_path):
    idx = VersionedIndex(str(tmp_path), FakeRetriever())
    idx.add_version("v1", snippets=chunk_source(V1, "a.py"))
    again = VersionedIndex(str(tmp_path), FakeRetriever())
    assert again.order == ["v1"] and len(again.hashes) == 3
