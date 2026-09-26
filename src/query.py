"""Ask a natural-language question, get ranked code snippets.

    python -m src.query --store .index/myrepo "how is the input parsed?"
    python -m src.query --store .index/myrepo --version v1 "..."
    python -m src.query --store .index/myrepo --version all "..."   # across every version
    python -m src.query --store .index/myrepo -i                     # interactive

    python -m src.query --apps "Given n integers, print the largest..."  # search the APPS corpus
"""
from __future__ import annotations

import argparse
import os
import sys
import textwrap
import time

from .config import DEFAULT
from .retriever import CodeRetriever
from .versioned_index import VersionedIndex

C = dict(b="\033[1m", d="\033[2m", g="\033[32m", c="\033[36m", y="\033[33m", r="\033[0m") \
    if sys.stdout.isatty() else dict(b="", d="", g="", c="", y="", r="")


def show(hits, dt, lines):
    print(f"{C['d']}{len(hits)} results in {dt * 1000:.0f} ms (CPU){C['r']}")
    for i, h in enumerate(hits, 1):
        loc = f"{h.path}:{h.start}-{h.end}" if h.path else h.id
        ver = f"  {C['y']}[{h.version}]{C['r']}" if h.version else ""
        also = f" {C['d']}(identical in {', '.join(h.also_in)}){C['r']}" if h.also_in else ""
        print(f"\n{C['b']}#{i}{C['r']}  {C['g']}{h.score:.3f}{C['r']}  {C['c']}{loc}{C['r']}  {h.name}{ver}{also}")
        body = h.code.splitlines()
        for l in body[:lines]:
            print("    " + l)
        if len(body) > lines:
            print(f"    {C['d']}... {len(body) - lines} more lines{C['r']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?")
    ap.add_argument("--store", help="index directory built by src.index")
    ap.add_argument("--apps", action="store_true", help="search the APPS benchmark corpus")
    ap.add_argument("--version", help="version label, or 'all' (default: latest)")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--lines", type=int, default=12, help="lines of code to print per hit")
    ap.add_argument("-i", "--interactive", action="store_true")
    a = ap.parse_args()

    r = CodeRetriever(DEFAULT)
    if a.apps:
        from .apps_index import apps_index
        idx = apps_index(r)
    else:
        if not a.store:
            ap.error("--store or --apps required")
        idx = VersionedIndex(a.store, r)
    _ = r.model  # load weights before timing queries
    print(f"{C['d']}model {DEFAULT.model} loaded in {r.load_s:.1f}s · "
          f"{len(idx.hashes)} snippets · versions: {', '.join(idx.order)}{C['r']}")

    def run(q):
        t0 = time.time()
        hits = idx.search(q, version=a.version, k=a.k)
        show(hits, time.time() - t0, a.lines)

    if a.query:
        run(a.query)
    if a.interactive or not a.query:
        while True:
            try:
                q = input(f"\n{C['b']}query>{C['r']} ").strip()
            except (EOFError, KeyboardInterrupt):
                print(); break
            if q:
                run(q)


if __name__ == "__main__":
    main()
