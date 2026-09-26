"""The APPS benchmark corpus (8,765 Python solutions) as a searchable index, for demos."""
from __future__ import annotations

import os

from .chunking import Snippet
from .versioned_index import VersionedIndex

STORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".index", "apps")


def apps_index(retriever, store: str = STORE) -> VersionedIndex:
    idx = VersionedIndex(store, retriever)
    if "apps" not in idx.versions:
        import mteb
        task = mteb.get_task("AppsRetrieval"); task.load_data()
        corpus = task.dataset["default"]["test"]["corpus"]
        snippets = [Snippet(x["id"], "", x["id"], 1, x["text"].count("\n") + 1, x["text"]) for x in corpus]
        print(f"embedding {len(snippets)} APPS solutions once (cached in {store}) ...")
        idx.add_version("apps", snippets=snippets)
    return idx
