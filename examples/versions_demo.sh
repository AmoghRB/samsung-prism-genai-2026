#!/usr/bin/env bash
# P1 + Bonus demo: index three releases of a real Python library, then search
# one version, the latest, and all versions at once.
#
#   bash examples/versions_demo.sh            # reuses an existing index (fast)
#   bash examples/versions_demo.sh --rebuild  # re-embeds all three versions (~8 min on CPU)
set -euo pipefail
cd "$(dirname "$0")/.."

REPO=.cache/requests
STORE=.index/requests
if [[ ! -d $REPO ]]; then
  # full clone: `git archive` on a blobless clone fetches lazily and can fail mid-run
  git clone --quiet https://github.com/psf/requests.git "$REPO"
fi
if [[ ${1:-} == --rebuild || ! -d $STORE ]]; then
  rm -rf "$STORE"
  echo "== index v2.28.0 (cold: every snippet embedded)"
  python -m src.index --git "$REPO" --revs v2.28.0 --store "$STORE"
  echo "== index v2.31.0 and v2.32.3 (incremental: only changed snippets embedded)"
  python -m src.index --git "$REPO" --revs v2.31.0 v2.32.3 --store "$STORE"
fi
echo "== indexed versions"
python -m src.index --store "$STORE" --list

Q="where are proxy credentials stripped from headers on redirect"
echo; echo "== latest version"; python -m src.query --store "$STORE" -k 3 --lines 6 "$Q"
echo; echo "== pinned to v2.28.0"; python -m src.query --store "$STORE" --version v2.28.0 -k 3 --lines 6 "$Q"
echo; echo "== across all versions (evolutionary)"; python -m src.query --store "$STORE" --version all -k 3 --lines 6 "$Q"
