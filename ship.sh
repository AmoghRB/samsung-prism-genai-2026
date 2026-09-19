#!/usr/bin/env bash
# ship.sh — the daily push. Run from inside a project folder:
#   ./ship.sh "what I did today"
set -euo pipefail

MSG="${*:-}"

if [[ -z "$MSG" ]]; then
  echo "usage: ./ship.sh \"what I did today\"" >&2
  exit 1
fi

# Must be inside a git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: not a git repository. Run 'git init' first (see WORKFLOW.md)." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Nothing to do? Say so rather than making an empty commit.
if [[ -z "$(git status --porcelain)" ]]; then
  echo "nothing to commit — working tree is clean."
  exit 0
fi

echo "--- changes ---"
git status --short
echo

# Log it before staging, so PROGRESS.md goes in the same commit
TODAY="$(date +%Y-%m-%d)"
if [[ -f PROGRESS.md ]]; then
  printf '\n- **%s** — %s\n' "$TODAY" "$MSG" >> PROGRESS.md
  echo "logged to PROGRESS.md"
fi

git add -A
git commit -m "$MSG"

# Push. Set upstream automatically on the first push.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if git remote get-url origin >/dev/null 2>&1; then
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    git push
  else
    git push -u origin "$BRANCH"
  fi
  echo
  echo "pushed to $(git remote get-url origin) [$BRANCH]"
else
  echo
  echo "committed locally, but no 'origin' remote is set — nothing was pushed." >&2
  echo "add one with:  git remote add origin git@github.com:AmoghRB/<repo>.git" >&2
  exit 1
fi
