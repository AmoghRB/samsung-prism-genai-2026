"""Turn a Python codebase into retrievable snippets.

APPS solutions are whole programs, so for the benchmark each document is one
snippet. For a real repository we split on top-level functions/classes with
`ast`, keeping the module header (imports, globals) as its own snippet, so a
query lands on the block of code that answers it rather than on a 2,000-line
file.
"""
from __future__ import annotations

import ast
import hashlib
import os
from dataclasses import dataclass, asdict


@dataclass
class Snippet:
    id: str            # stable identity across versions: path::qualname
    path: str
    name: str          # qualified name, or "<module>" for the header
    start: int         # 1-based line numbers
    end: int
    code: str

    @property
    def hash(self) -> str:
        return hashlib.sha1(self.code.encode("utf-8", "replace")).hexdigest()

    def to_dict(self) -> dict:
        d = asdict(self); d["hash"] = self.hash
        return d


def chunk_source(source: str, path: str) -> list[Snippet]:
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Unparseable file: index it whole rather than drop it.
        return [Snippet(f"{path}::<file>", path, "<file>", 1, len(lines), source)] if source.strip() else []

    out: list[Snippet] = []
    covered: set[int] = set()

    def add(node, qual):
        start = min([d.lineno for d in getattr(node, "decorator_list", [])] + [node.lineno])
        end = node.end_lineno or node.lineno
        out.append(Snippet(f"{path}::{qual}", path, qual, start, end, "\n".join(lines[start - 1:end])))
        covered.update(range(start, end + 1))

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add(node, node.name)
        elif isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            # Small classes stay whole; large ones are split per method so each
            # method is independently retrievable.
            if len(methods) > 1 and (node.end_lineno - node.lineno) > 60:
                for m in methods:
                    add(m, f"{node.name}.{m.name}")
            else:
                add(node, node.name)

    rest = [i for i in range(1, len(lines) + 1) if i not in covered and lines[i - 1].strip()]
    if rest:
        body = "\n".join(lines[i - 1] for i in rest)
        out.insert(0, Snippet(f"{path}::<module>", path, "<module>", rest[0], rest[-1], body))
    return out


def chunk_directory(root: str, exts=(".py",)) -> list[Snippet]:
    snippets: list[Snippet] = []
    skip = {".git", ".venv", "venv", "__pycache__", "node_modules", ".index"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in skip)
        for fn in sorted(filenames):
            if fn.endswith(exts):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root)
                with open(full, encoding="utf-8", errors="replace") as f:
                    snippets.extend(chunk_source(f.read(), rel))
    return snippets
