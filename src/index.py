"""Index a codebase version (P1).

    python -m src.index --src path/to/repo --version v1 --store .index/myrepo
    python -m src.index --src path/to/repo --version v2 --store .index/myrepo   # incremental
    python -m src.index --store .index/myrepo --list

Or index a git repository at several commits in one go:

    python -m src.index --git path/to/repo --revs v1.0 v1.1 HEAD --store .index/myrepo
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile

from .config import DEFAULT
from .retriever import CodeRetriever
from .versioned_index import VersionedIndex


def _checkout(repo: str, rev: str, dest: str):
    # `git archive` exports a commit without touching the user's working tree
    p = subprocess.run(["git", "-C", repo, "archive", "--format=tar", rev], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git archive {rev} failed: {p.stderr.decode().strip()}")
    subprocess.run(["tar", "-x", "-C", dest], input=p.stdout, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", required=True, help="index directory")
    ap.add_argument("--src", help="source directory to index as one version")
    ap.add_argument("--version", help="version label for --src (default: directory name)")
    ap.add_argument("--git", help="git repository to index at --revs")
    ap.add_argument("--revs", nargs="+", help="commits/tags to index")
    ap.add_argument("--list", action="store_true", help="list indexed versions")
    a = ap.parse_args()

    idx = VersionedIndex(a.store, CodeRetriever(DEFAULT))
    if a.list:
        for v in idx.order:
            print(f"{v:20s} {len(idx.versions[v]):6d} snippets")
        print(f"{len(idx.hashes)} unique snippet bodies embedded")
        return
    if a.src:
        print(json.dumps(idx.add_version(a.version or os.path.basename(os.path.abspath(a.src)), root=a.src)))
    if a.git:
        for rev in a.revs or ["HEAD"]:
            with tempfile.TemporaryDirectory() as tmp:
                _checkout(a.git, rev, tmp)
                print(json.dumps(idx.add_version(rev, root=tmp)))


if __name__ == "__main__":
    main()
