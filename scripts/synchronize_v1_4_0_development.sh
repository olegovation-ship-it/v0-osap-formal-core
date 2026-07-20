#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
if [[ "$MODE" != "baseline" && "$MODE" != "final" ]]; then
  echo "Usage: $0 baseline|final" >&2
  exit 2
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: working tree must be clean." >&2
  exit 1
fi

git fetch origin --prune
BASELINE="46c02d96c047e70fe0d54feb60a0aadce2de95c7"
MAIN_REF="refs/remotes/origin/main"
DEV_REF="refs/remotes/origin/v1.4.0-development"
MAIN_SHA="$(git rev-parse "$MAIN_REF")"

if ! git merge-base --is-ancestor "$BASELINE" "$MAIN_SHA"; then
  echo "ERROR: origin/main does not contain the WP0 merge baseline." >&2
  exit 1
fi

if git show-ref --verify --quiet "$DEV_REF"; then
  git switch v1.4.0-development
else
  git switch -c v1.4.0-development --track origin/v1.4.0-development
fi

git merge --ff-only origin/main
git push origin v1.4.0-development

git switch main
git pull --ff-only origin main
git fetch origin --prune

MAIN_SHA="$(git rev-parse refs/remotes/origin/main)"
DEV_SHA="$(git rev-parse refs/remotes/origin/v1.4.0-development)"
printf 'mode=%s
origin/main=%s
origin/v1.4.0-development=%s
' "$MODE" "$MAIN_SHA" "$DEV_SHA"

if [[ "$MAIN_SHA" != "$DEV_SHA" ]]; then
  echo "ERROR: branch synchronization did not produce ref equality." >&2
  exit 1
fi

echo "V1_4_0_DEVELOPMENT_BRANCH_SYNCHRONIZATION_PASS"
