"""Query and snippet pre-processing.

APPS queries are full competitive-programming statements: a story, then
`-----Input-----` / `-----Output-----` format sections, then worked examples.
Code solutions mostly mirror the *input/output format* (how many ints are read,
what gets printed) and the *core task*, not the story or the example numbers.
So the query is re-assembled from its sections with the informative parts
first, and noise (LaTeX `$...$`, long digit dumps from examples, notes,
repeated whitespace) is removed before it reaches the encoder's token budget.
"""
from __future__ import annotations

import re

_SECTION = re.compile(r"-{3,}\s*([A-Za-z ]+?)\s*-{3,}")


def split_sections(q: str) -> dict[str, str]:
    parts = _SECTION.split(q)
    out = {"statement": parts[0]}
    for i in range(1, len(parts) - 1, 2):
        out[parts[i].strip().lower()] = parts[i + 1]
    return out


def _clean(t: str) -> str:
    t = re.sub(r"\$\$?([^$]*)\$\$?", r"\1", t)            # $x$ -> x
    t = re.sub(r"\\(le|leq)\b", "<=", t)
    t = re.sub(r"\\(ge|geq)\b", ">=", t)
    t = re.sub(r"\\(cdot|times)\b", "*", t)
    t = re.sub(r"\\ldots|\\dots", "...", t)
    t = re.sub(r"\\[a-zA-Z]+", " ", t)                     # other LaTeX commands
    t = re.sub(r"[{}]", "", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def preprocess_query(q: str, mode: str = "clean") -> str:
    if mode == "raw":
        return q
    if mode == "clean":
        return _clean(q)
    s = split_sections(q)
    stmt = _clean(s.get("statement", ""))
    io = "\n".join(_clean(s[k]) for k in ("input", "output") if k in s)
    ex_key = next((k for k in s if k.startswith("example")), None)
    ex = _clean(s[ex_key])[:400] if ex_key else ""
    if mode == "noex":          # statement + I/O spec, no examples / notes
        return f"{stmt}\n{io}".strip()
    if mode == "iofirst":       # I/O spec leads so it survives truncation
        return f"{io}\n{stmt}\n{ex}".strip()
    raise ValueError(mode)


def preprocess_code(c: str, mode: str = "raw") -> str:
    if mode == "raw":
        return c
    if mode == "strip":
        # drop commented-out debug lines and blank lines; keep real comments short
        lines = [l for l in c.splitlines() if l.strip() and not re.match(r"\s*#\s*print", l)]
        return "\n".join(lines)
    raise ValueError(mode)
